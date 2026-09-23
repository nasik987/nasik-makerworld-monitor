#!/usr/bin/env python3
"""Per-model MakerWorld monitoring using FetchLayer public endpoints."""
import json, os, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

UID="506781369"
BASE="https://api.fetchlayer.dev/makerworld"
CATALOG=Path("data/models.json")
HISTORY=Path("data/model-history.json")
LATEST=Path("data/model-latest.json")

def post(endpoint, payload, key):
    req=urllib.request.Request(
        f"{BASE}/{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def load(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def main():
    key=os.environ.get("FETCHLAYER_API_KEY","").strip()
    if not key:
        sys.exit("Chybí FETCHLAYER_API_KEY.")

    profile=post("designer-profile", {"designer":UID}, key).get("profile",{})
    if str(profile.get("uid")) != UID:
        sys.exit("Neočekávaný profil.")

    catalog=load(CATALOG, {"models":{}})
    if not isinstance(catalog,dict):
        catalog={"models":{}}
    models=catalog.setdefault("models",{})

    pinned_ids=[str(x) for x in profile.get("pinnedModelIds",[]) if x is not None]
    pinned=profile.get("pinnedModels",[])
    pinned_by_id={str(m.get("modelId") or m.get("id")):m for m in pinned if isinstance(m,dict)}

    for mid in pinned_ids:
        info=models.setdefault(mid,{})
        p=pinned_by_id.get(mid,{})
        info.setdefault("title", p.get("title") or f"Model {mid}")
        info["source"]="designer-profile:pinned"
        info["enabled"]=True

    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    snapshot={"time_utc":now,"uid":UID,"models":{},"notes":[]}

    for mid,meta in sorted(models.items()):
        if meta.get("enabled",True) is False:
            continue
        try:
            result=post("model-detail", {"model":str(mid),"printProfileLimit":1}, key)
            model=result.get("model") or {}
            stats=model.get("stats") or {}
            creator=model.get("designer") or model.get("designCreator") or {}
            creator_uid=str(creator.get("uid") or creator.get("userId") or "")
            if creator_uid and creator_uid != UID:
                snapshot["notes"].append(f"{mid}: přeskočeno, jiný autor {creator_uid}")
                continue

            title=model.get("title") or meta.get("title") or f"Model {mid}"
            meta["title"]=title
            meta["url"]=result.get("requestedUrl") or meta.get("url")

            metrics={}
            for k in ("downloadCount","printCount","likeCount","collectionCount",
                      "boostCount","commentCount","shareCount"):
                v=stats.get(k)
                metrics[k]=v if type(v) is int and v>=0 else None

            snapshot["models"][str(mid)]={"title":title,"metrics":metrics}
        except Exception as exc:
            snapshot["notes"].append(f"{mid}: {type(exc).__name__}")

    history=load(HISTORY,[])
    if not isinstance(history,list):
        history=[]
    history.append(snapshot)

    # ~90 dní při 3h intervalu
    if len(history)>720:
        history=history[-720:]

    CATALOG.parent.mkdir(parents=True,exist_ok=True)
    catalog["updated_utc"]=now
    catalog["profile_model_count"]=profile.get("modelCount")

    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    HISTORY.write_text(json.dumps(history,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    LATEST.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    print(f"Hotovo: {len(snapshot['models'])} modelů, {len(snapshot['notes'])} upozornění.")

if __name__=="__main__":
    main()
