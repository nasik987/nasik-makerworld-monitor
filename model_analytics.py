import json
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).parent
H=ROOT/"data/model-history.json"
OUT=ROOT/"data/model-analytics.md"

def dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def load():
    try:
        return json.loads(H.read_text(encoding="utf-8"))
    except Exception:
        return []

def metric(snap,mid,k):
    v=snap.get("models",{}).get(mid,{}).get("metrics",{}).get(k)
    return v if type(v) is int else None

def prior(history, latest, hours):
    target=dt(latest["time_utc"]).timestamp()-hours*3600
    candidates=[s for s in history[:-1] if dt(s["time_utc"]).timestamp()<=target]
    return candidates[-1] if candidates else (history[0] if len(history)>1 else None)

def delta(a,b,mid,k):
    if not a:
        return None
    x,y=metric(a,mid,k),metric(b,mid,k)
    return y-x if x is not None and y is not None else None

def f(v):
    return "—" if v is None else f"{v:+d}" if isinstance(v,int) else str(v)

history=load()
lines=["# NASIK – model analytics",""]

if not history:
    lines+=["Zatím nejsou per-model data."]
else:
    latest=history[-1]
    p24=prior(history,latest,24)
    p7=prior(history,latest,24*7)
    rows=[]

    for mid,m in latest.get("models",{}).items():
        d24=delta(p24,latest,mid,"downloadCount")
        p24d=delta(p24,latest,mid,"printCount")
        l24=delta(p24,latest,mid,"likeCount")
        b24=delta(p24,latest,mid,"boostCount")
        c24=delta(p24,latest,mid,"commentCount")
        score=sum(x*w for x,w in [(d24,1),(p24d,2),(l24,1),(b24,10),(c24,3)] if isinstance(x,int))
        d7=delta(p7,latest,mid,"downloadCount")

        rows.append((
            score,mid,m.get("title",mid),
            metric(latest,mid,"downloadCount"),
            d24,p24d,l24,b24,d7
        ))

    rows.sort(reverse=True)

    lines += [
        f"Poslední měření: {latest['time_utc']}",
        f"Sledovaných modelů: {len(rows)}","",
        "## Momentum – posledních 24 hodin","",
        "| Model | Downloads | Δ24h | Prints Δ24h | Likes Δ24h | Boosts Δ24h | Δ7d downloads | Momentum |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]

    for score,mid,title,total,d24,p24d,l24,b24,d7 in rows:
        lines.append(
            f"| {title} | {total if total is not None else '—'} | {f(d24)} | "
            f"{f(p24d)} | {f(l24)} | {f(b24)} | {f(d7)} | {score} |"
        )

    lines += [
        "",
        "Momentum = Δdownloads + 2×Δprints + Δlikes + 10×Δboosts + 3×Δcomments.",
        "Je to interní NASIK metrika, nikoli MakerWorld ranking ani odhad bodů.",
        "",
        "## Poznámka",
        "",
        "První verze automaticky sleduje připnuté modely a všechny ručně přidané modely v data/models.json."
    ]

OUT.parent.mkdir(exist_ok=True)
OUT.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(OUT)
