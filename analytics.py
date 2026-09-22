import json
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).parent
history=ROOT/'data/history.json'
records=json.loads(history.read_text(encoding='utf-8')) if history.exists() else []
records=sorted((r for r in records if isinstance(r,dict) and r.get('time_utc') and isinstance(r.get('metrics'),dict)),key=lambda r:r['time_utc'])
labels={'downloadCount':'Stažení','printCount':'Tisky','followerCount':'Sledující','likeCount':'Lajky','boostCount':'Boosty','modelCount':'Modely'}
def val(r,k):
 v=r.get('metrics',{}).get(k)
 return v if type(v)==int and v>=0 else None
def fmt(v):return f'{v:,.2f}'.replace(',',' ').replace('.',',') if isinstance(v,float) else f'{v:,}'.replace(',',' ') if v is not None else 'nedostupné'
def days(a,b):return (datetime.fromisoformat(b['time_utc'].replace('Z','+00:00'))-datetime.fromisoformat(a['time_utc'].replace('Z','+00:00'))).total_seconds()/86400
lines=['# NASIK Analytics','','Automatická analýza historických měření.']
if records:
 latest=records[-1];lines+=['',f"Poslední měření: {latest['time_utc']}",f'Počet měření: {len(records)}','','## Aktuální stav','','| Metrika | Hodnota |','|---|---:|']
 for k,label in labels.items():lines.append(f'| {label} | {fmt(val(latest,k))} |')
 lines+=['','## Tempo růstu za 24 hodin','','| Metrika | Poslední interval | Dostupná data za 7 dní | Dostupná data za 30 dní |','|---|---:|---:|---:|']
 for k,label in labels.items():
  rates=[]
  for window in (None,7,30):
   eligible=[r for r in records[:-1] if days(r,latest)>0 and (window is None or days(r,latest)<=window)]
   old=(eligible[-1] if window is None else eligible[0]) if eligible else None
   a,b=(val(old,k),val(latest,k)) if old else (None,None)
   rates.append((b-a)/days(old,latest) if a is not None and b is not None else None)
  lines.append(f'| {label} | '+' | '.join(fmt(x) for x in rates)+' |')
 lines+=['','## Poměry','','| Ukazatel | Hodnota |','|---|---:|']
 downloads=val(latest,'downloadCount');models=val(latest,'modelCount')
 for k,label in [('printCount','Tisky / stažení'),('likeCount','Lajky / stažení'),('boostCount','Boosty / stažení')]:
  x=val(latest,k);lines.append(f'| {label} | {fmt(100*x/downloads) if downloads and x is not None else "nedostupné"} % |')
 for k,label in [('downloadCount','Stažení na model'),('printCount','Tisky na model'),('likeCount','Lajky na model')]:
  x=val(latest,k);lines.append(f'| {label} | {fmt(x/models) if models and x is not None else "nedostupné"} |')
 lines+=['','## Milníky','','| Milník | Zbývá |','|---|---:|']
 for k,target,label in [('downloadCount',100000,'100 000 stažení'),('printCount',50000,'50 000 tisků'),('followerCount',4000,'4 000 sledujících')]:
  x=val(latest,k);lines.append(f'| {label} | {fmt(max(0,target-x)) if x is not None else "nedostupné"} |')
else:lines+=['','Zatím žádná měření.']
lines+=['','## Omezení','','- Poměry čítačů nejsou konverze unikátních uživatelů.','- Průměry na model nejsou mediány.','- Sedmidenní a třicetidenní tempo používá pouze dostupné body v okně; nemusí pokrývat celé období.','- Bez samostatných dat modelů nelze určit jejich pořadí ani výkon.','']
output=ROOT/'data/analytics.md';output.parent.mkdir(exist_ok=True);output.write_text('\n'.join(lines),encoding='utf-8');print(output)
