# MakerWorld Nasik – automatické statistiky

Denně se provede **1 dotaz** na FetchLayer `POST /makerworld/designer-profile` pro UID `506781369`. Výsledek se přidá do `data/history.json` a čitelný přehled s rozdílem proti předchozímu měření se uloží do `data/latest-report.md`.

## Zprovoznění

1. Původní API klíč, který byl vložen do chatu, zneplatni ve FetchLayer a vygeneruj nový.
2. Vytvoř na GitHubu **soukromý repozitář** a nahraj do jeho kořene obsah této složky (včetně skryté složky `.github`).
3. V repozitáři otevři **Settings → Secrets and variables → Actions → New repository secret**. Název: `FETCHLAYER_API_KEY`, hodnota: nový klíč. Nepřidávej klíč do kódu, souborů, issue ani chatu.
4. V **Actions → Nasik MakerWorld daily statistics → Run workflow** spusť první sběr ručně. Výsledky najdeš v `data/latest-report.md`; při další kontrole se doplní rozdíly.
5. Workflow běží každý den přibližně v **08:17 Europe/Prague**. GitHub může plánované spuštění opozdit. Umožni GitHub Actions zapisovat do repozitáře v **Settings → Actions → General → Workflow permissions → Read and write permissions**, pokud zápis selže.

**Důležitá omezení:** Tento projekt nepřeposílá zprávy automaticky do ChatGPT ani e-mailu. Poskytuje trvalý report na GitHubu, který lze dále napojit. API `designer-profile` obsahuje souhrnné počty a připnuté modely, **ne kompletní katalog všech modelů**; proto nejsou slibovány denní žebříčky jednotlivých modelů. Některé metriky mohou být nedostupné (zobrazí se „nedostupné“). Při výpadku API se historie nepřepisuje. Počet kreditů závisí na aktuálním ceníku FetchLayer.
