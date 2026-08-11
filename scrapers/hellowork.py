from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from scrapers.utils import USER_AGENT, accepter_cookies, nettoyer

NOM_SOURCE = "Hellowork"

URL_RECHERCHE = "https://www.hellowork.com/fr-fr/emploi/recherche.html"
# Identifiant interne "commune" de Rochefort côté Hellowork/RegionsJob (même code que France Travail : 17299)
FRAGMENT_ID_ROCHEFORT = "/commune/17299"


def _fermer_popins(page):
    accepter_cookies(page)
    try:
        bouton = page.locator('[data-cy="closeHWOneTap"]')
        if bouton.count() > 0 and bouton.first.is_visible():
            bouton.first.click(timeout=3000)
            page.wait_for_timeout(500)
    except Exception:
        pass


def scraper():
    """Recherche les offres autour de Rochefort sur Hellowork, puis ne garde que
    celles réellement situées à Rochefort (le filtre de rayon exact est caché
    derrière un accordéon replié, donc on filtre côté client à la place)."""
    offres = []
    horodatage = datetime.now(timezone.utc).isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(URL_RECHERCHE, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        _fermer_popins(page)

        champ_lieu = page.locator("#l")
        champ_lieu.click()
        champ_lieu.fill("")
        champ_lieu.type("Rochefort", delay=80)
        page.wait_for_timeout(1500)

        suggestion = page.locator(f'button[data-autocomplete-id-param*="{FRAGMENT_ID_ROCHEFORT}"]')
        if suggestion.count() == 0:
            browser.close()
            return offres
        suggestion.first.click()
        page.wait_for_timeout(1000)

        page.click('[data-cy="searchEngineSubmitButton"]')
        page.wait_for_timeout(3000)

        cartes = page.locator("li[data-id-storage-item-id]")
        nb = cartes.count()

        for i in range(nb):
            carte = cartes.nth(i)
            id_offre = carte.get_attribute("data-id-storage-item-id")

            try:
                titre = carte.locator('input[name="title"]').first.input_value()
                entreprise = carte.locator('input[name="company"]').first.input_value()
            except Exception:
                continue

            try:
                lieu = nettoyer(carte.locator('[data-cy="localisationCard"]').first.inner_text())
            except Exception:
                lieu = ""

            # Filtre "lieu exact" : on écarte les communes voisines (Tonnay-Charente, etc.)
            if not lieu.lower().startswith("rochefort"):
                continue

            try:
                contrat = nettoyer(carte.locator('[data-cy="contractCard"]').first.inner_text())
            except Exception:
                contrat = ""

            try:
                lien_relatif = carte.locator('[data-cy="offerTitle"]').first.get_attribute("href")
                url = f"https://www.hellowork.com{lien_relatif}" if lien_relatif else ""
            except Exception:
                url = ""

            try:
                date_pub = nettoyer(carte.locator("div.text-grey-500").last.inner_text())
            except Exception:
                date_pub = ""

            offres.append({
                "id_offre": id_offre,
                "source": NOM_SOURCE,
                "titre": nettoyer(titre),
                "entreprise": nettoyer(entreprise),
                "lieu": lieu,
                "contrat": contrat,
                "temps_travail": "",
                "description": "",
                "date_publication": date_pub,
                "url": url,
                "date_scraping": horodatage,
            })

        browser.close()

    return offres
