# NASIK Analytics – instalace

1. Rozbal ZIP.
2. Nahraj soubor `analytics.py` do kořene repozitáře (GitHub → Add file → Upload files). Nenahrávej soubor README-UPDATE.md ani adresář data.
3. Otevři `.github/workflows/daily.yml`, klikni na tužku a přidej pod krok `Collect MakerWorld statistics` nový krok:

```yaml
      - name: Generate analytics
        run: python analytics.py
```

Krok musí být před `Save statistics`, který už ukládá `data/`.
4. Commit changes a v Actions spusť workflow ručně. Výsledek: `data/analytics.md`.

Není třeba měnit API klíč ani historická data. Tento balíček nesbírá jednotlivé modely: endpoint původního monitoru kompletní katalog neposkytuje a neověřené API endpointy záměrně nevoláme. Sběr modelů bude vyžadovat ověřený zdroj dat.
