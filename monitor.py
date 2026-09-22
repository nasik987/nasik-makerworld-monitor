#!/usr/bin/env python3
"""One FetchLayer designer-profile request per run, no third-party dependencies."""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

UID = '506781369'
ENDPOINT = 'https://api.fetchlayer.dev/makerworld/designer-profile'
DATA = Path('data/history.json')
REPORT = Path('data/latest-report.md')
FIELDS = [('followerCount', 'Sledující'), ('modelCount', 'Modely'),
          ('downloadCount', 'Stažení'), ('printCount', 'Tisky'),
          ('likeCount', 'Lajky'), ('boostCount', 'Boosty')]


def get_data(key):
    payload = json.dumps({'designer': UID}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=payload,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def format_value(value):
    return f'{value:,}'.replace(',', ' ') if isinstance(value, int) else 'nedostupné'


def main():
    key = os.environ.get('FETCHLAYER_API_KEY', '').strip()
    if not key:
        sys.exit('Chybí GitHub Secret FETCHLAYER_API_KEY; žádná data nebyla změněna.')
    try:
        result = get_data(key)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        sys.exit(f'API požadavek selhal: {type(exc).__name__}; historická data zůstala nedotčená.')
    profile = result.get('profile')
    if not isinstance(profile, dict) or str(profile.get('uid')) != UID:
        sys.exit('API nevrátilo očekávané UID; historická data zůstala nedotčená.')
    notes = result.get('notes', [])
    if not isinstance(notes, list):
        notes = ['API vrátilo neobvyklé pole notes.']
    values = {k: profile.get(k) if type(profile.get(k)) is int and profile[k] >= 0 else None for k, _ in FIELDS}
    if not any(v is not None for v in values.values()):
        sys.exit('API nevrátilo žádnou použitelnou statistiku; historie nedotčená.')
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    records = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else []
    if not isinstance(records, list):
        sys.exit('Neplatný formát souboru historie.')
    previous = records[-1] if records else None
    record = {'time_utc': now, 'uid': UID, 'metrics': values, 'notes': notes}
    records.append(record)
    lines = ['# Nasik – denní MakerWorld report', '', f'Měření UTC: {now}',
             f'Profil: https://makerworld.com/cs/@user_{UID}', '',
             '| Ukazatel | Stav | Změna od minulého měření |', '|---|---:|---:|']
    for key_name, label in FIELDS:
        new = values[key_name]
        old = previous.get('metrics', {}).get(key_name) if previous else None
        if isinstance(new, int) and type(old) is int:
            delta = new - old
            change = f'{delta:+d}' if delta >= 0 else f'{delta:d} (pokles / revize hodnot)'
        else:
            change = 'bez srovnání'
        lines.append(f'| {label} | {format_value(new)} | {change} |')
    lines.extend(['', 'Porovnání je proti předchozímu úspěšnému měření, nikoli nutně přesně 24 hodin.'])
    if previous:
        lines.append(f'Předchozí měření UTC: {previous["time_utc"]}.')
    if notes:
        lines.extend(['', '## Upozornění API'] + [f'- {str(n)}' for n in notes])
    lines.extend(['', '## Rozsah', 'FetchLayer designer-profile poskytuje souhrn profilu a připnuté modely, nikoli úplný seznam všech modelů. Tento report neslibuje růst jednotlivých modelů ani automatickou zprávu do ChatGPT.', ''])
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print('Hotovo: data/history.json a data/latest-report.md aktualizovány.')


if __name__ == '__main__':
    main()
