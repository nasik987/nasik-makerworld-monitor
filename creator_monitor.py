#!/usr/bin/env python3
import os, json, html, re, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE="https://makerworld.com"
PAGE="/cs/my/data-overview/model"
OUT_DIR=Path("data")
HISTORY=OUT_DIR/"creator-history.json"
LATEST=OUT_DIR/"creator-latest.json"
CATALOG=OUT_DIR/"creator-models.json"

def fetch_page(start_date, end_date, cookie):
    qs=urllib.parse.urlencode({"startDate":start_date,"endDate":end_date})
    url=f"{BASE}{PAGE}?{qs}"
    req=urllib.request.Request(url, headers={
        "Cookie":cookie,
        "User-Agent":"Mozilla/5.0",
        "Accept-Language":"cs-CZ,cs;q=0.9,en;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8","replace"), url

def extract_next_data(page_html):
    m=re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', page_html, re.S|re.I)
    if not m:
        raise RuntimeError("Na stránce nebyl nalezen __NEXT_DATA__.")
    return json.loads(html.unescape(m.group(1)))

def normalize_model(m):
    def num(k):
        v=m.get(k)
        return v if isinstance(v,(int,float)) else None
    return {
        "designId":m.get("designId"),
        "title":m.get("title"),
        "publishTime":m.get("publishTime"),
        "impression":num("impression"),
        "view":num("view"),
        "like":num("like"),
        "collect":num("collect"),
        "print":num("print"),
        "download":num("download"),
        "point":num("point"),
        "boost":num("boost"),
        "pointRegular":m.get("pointRegular"),
        "pointExclusive":m.get("pointExclusive"),
        "boostRegular":m.get("boostRegular"),
        "boostExclusive":m.get("boostExclusive"),
    }

def main():
    cookie=os.environ.get("MAKERWORLD_COOKIE","").strip()
    if not cookie:
        raise SystemExit("Chybí GitHub Secret MAKERWORLD_COOKIE.")

    today=datetime.now(timezone.utc).date()
    yesterday=today-timedelta(days=1)

    snapshots=[]
    for day in (yesterday,today):
        page,url=fetch_page(day.isoformat(),day.isoformat(),cookie)
        data=extract_next_data(page)
        props=data.get("props",data).get("pageProps",data.get("pageProps",{}))
        summary=props.get("statisticalData",{}).get("summary",{})
        models=[normalize_model(x) for x in props.get("statisticalList",[]) if isinstance(x,dict)]
        snapshots.append({
            "day":day.isoformat(),
            "fetched_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_url":url,
            "summary":summary,
            "models":models
        })

    OUT_DIR.mkdir(exist_ok=True)
    latest={"today":snapshots[1],"yesterday":snapshots[0]}
    LATEST.write_text(json.dumps(latest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    hist=[]
    if HISTORY.exists():
        try:
            hist=json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception:
            hist=[]
    if not isinstance(hist,list): hist=[]
    hist.append(latest)
    hist=hist[-300:]
    HISTORY.write_text(json.dumps(hist,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    catalog={}
    for snap in snapshots:
        for m in snap["models"]:
            mid=str(m.get("designId"))
            if mid!="None":
                catalog[mid]={
                    "title":m.get("title"),
                    "publishTime":m.get("publishTime")
                }
    CATALOG.write_text(json.dumps({
        "updated_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count":len(catalog),
        "models":catalog
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    print(f"Hotovo: dnes {len(snapshots[1]['models'])} modelů, včera {len(snapshots[0]['models'])} modelů.")

if __name__=="__main__":
    main()
