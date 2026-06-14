"""
explore_limitless.py
Script d'exploration de Limitless TCG pour comprendre la structure du site.
Sauvegarde le HTML brut et affiche les données clés trouvées.

Usage :
    python3 scripts/explore_limitless.py
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import json

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def explore():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        # ── 1. Intercepter les appels API au chargement ───────────────────
        print("Chargement de yugiohmeta.com/top-decks/ ...")
        api_calls = []

        def handle_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            if "json" in ct or any(x in url for x in ["/api/", ".json", "decks", "tier"]):
                api_calls.append((url, response.status))

        page.on("response", handle_response)
        page.goto("https://www.yugiohmeta.com/top-decks/", wait_until="networkidle")
        page.wait_for_timeout(3000)

        # Sauvegarde HTML
        html = page.content()
        Path("data/raw/yugiohmeta_topdecks.html").write_text(html, encoding="utf-8")
        print(f"  ✓ HTML sauvegardé ({len(html)} chars)")

        # Affiche les appels API détectés
        print(f"\n  Appels API/JSON détectés ({len(api_calls)}) :")
        for url, status in api_calls[:15]:
            print(f"    [{status}] {url}")

        # ── 2. Extraction du contenu visible ─────────────────────────────
        print("\nContenu visible sur la page :")
        decks = page.query_selector_all("a[href*='/top-decks/']")
        print(f"  Liens top-decks trouvés : {len(decks)}")
        for d in decks[:10]:
            href = d.get_attribute("href")
            text = d.inner_text().strip()
            if text:
                print(f"    - {text[:60]} → {href}")

        browser.close()


if __name__ == "__main__":
    explore()
