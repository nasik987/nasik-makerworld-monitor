import json
from pathlib import Path

ROOT=Path(__file__).parent
SRC=ROOT/"data/creator-latest.json"
OUT=ROOT/"data/creator-analytics.md"

def val(m,k):
    v=m.get(k)
    return v if isinstance(v,(int,float)) else 0

data=json.loads(SRC.read_text(encoding="utf-8"))
today=data["today"]
yest=data["yesterday"]

ymap={str(m["designId"]):m for m in yest["models"]}
rows=[]

for m in today["models"]:
    mid=str(m["designId"])
    y=ymap.get(mid,{})
    rows.append({
        "title":m.get("title") or mid,
        "points":val(m,"point"),
        "views":val(m,"view"),
        "impressions":val(m,"impression"),
        "downloads":val(m,"download"),
        "prints":val(m,"print"),
        "likes":val(m,"like"),
        "collects":val(m,"collect"),
        "boosts":val(m,"boost"),
        "y_points":val(y,"point"),
        "y_downloads":val(y,"download"),
        "y_prints":val(y,"print"),
    })

rows.sort(key=lambda r:(r["points"],r["downloads"],r["views"]), reverse=True)

s=today.get("summary",{})
lines=[
"# NASIK – Creator Center Analytics","",
f"Den: {today['day']}",
f"Modelů v dnešním výpisu: {len(rows)}","",
"## Souhrn dne","",
f"- Impressions: {s.get('impression','—')}",
f"- Views: {s.get('view','—')}",
f"- Downloads: {s.get('download','—')}",
f"- Prints: {s.get('print','—')}",
f"- Likes: {s.get('like','—')}",
f"- Collects: {s.get('collect','—')}",
f"- Points: {s.get('point','—')}",
f"- Boosts: {s.get('boost','—')}",
f"- Regular points: {s.get('pointRegular','—')}",
f"- Exclusive points: {s.get('pointExclusive','—')}",
"",
"## Modely dnes","",
"| Model | Points | Views | Impressions | Downloads | Prints | Likes | Collects | Boosts |",
"|---|---:|---:|---:|---:|---:|---:|---:|---:|"
]
for r in rows:
    lines.append(f"| {r['title']} | {r['points']} | {r['views']} | {r['impressions']} | {r['downloads']} | {r['prints']} | {r['likes']} | {r['collects']} | {r['boosts']} |")

OUT.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(OUT)
