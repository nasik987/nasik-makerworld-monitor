# NASIK monitor v3 – Creator Center

Tato verze už nepoužívá jen 6 připnutých modelů.

Skript se přihlásí přes MakerWorld session cookie uloženou v GitHub Secrets,
načte Creator Center stránku a z `__NEXT_DATA__` vytáhne:

- všechny modely v daném dni
- impressions
- views
- downloads
- prints
- likes
- collects
- points
- boosts
- regular/exclusive rozpad

## Instalace

Nahraj do kořene repozitáře:
- `creator_monitor.py`
- `creator_analytics.py`

Nahraj do:
- `.github/workflows/creator.yml`

Pak v GitHubu vytvoř Secret:
`MAKERWORLD_COOKIE`

Do něj vlož celý Cookie header z přihlášené MakerWorld relace.

DŮLEŽITÉ:
Cookie nikdy neposílej do chatu ani veřejně do repozitáře.
Patří pouze do GitHub Secrets.

Pak spusť:
Actions -> MakerWorld Nasik - Creator Center Monitor -> Run workflow
