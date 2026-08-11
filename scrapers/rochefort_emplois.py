import re
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from scrapers.utils import USER_AGENT, accepter_cookies, nettoyer

NOM_SOURCE = "Rochefort Emplois"

BASE = "https://www.rochefort-emplois.com"
URL_PAGE_1 = f"{BASE}/emploi/recherche.html"
URL_PAGE_N = BASE + "/emploi/recherche/{n}.html"

NB_PAGES = 2  # agrégateur déjà scopé sur Rochefort : 2 pages (~40 offres) suffisent pour une veille


def _extraire_id(href):
    m = re.search(r"/emplois/(\d+)\.html", href or "")
    return m.group(1) if m else href


def _scraper_une_page(page, url, horodatage):
    offres = []
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)
    accepter_cookies(page)

    cartes = page.locator("article.card-job-offer")
    nb = cartes.count()

    for i in range(nb):
        carte = cartes.nth(i)
        try:
            lien = carte.locator("h3 a").first
            titre = nettoyer(lien.inner_text())
            href = lien.get_attribute("href")
        except Exception:
            continue

        criteres = carte.locator("li.job-criteria-label span:nth-child(2)")
        lieu = nettoyer(criteres.nth(0).inner_text()) if criteres.count() > 0 else ""
        entreprise = nettoyer(criteres.nth(1).inner_text()) if criteres.count() > 1 else ""

        id_offre = _extraire_id(href)

        offres.append({
            "id_offre": id_offre,
            "source": NOM_SOURCE,
            "titre": titre,
            "entreprise": entreprise,
            "lieu": lieu,
            "contrat": "",
            "temps_travail": "",
            "description": "",
            "date_publication": "",
            "url": f"{BASE}{href}" if href else "",
            "date_scraping": horodatage,
        })

    return offres


def scraper():
    """Rochefort Emplois est un agrégateur déjà scopé sur le bassin rochefortais :
    pas de filtre géographique à appliquer, on parcourt juste les premières pages."""
    offres = []
    horodatage = datetime.now(timezone.utc).isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)

        offres += _scraper_une_page(page, URL_PAGE_1, horodatage)
        for n in range(2, NB_PAGES + 1):
            offres += _scraper_une_page(page, URL_PAGE_N.format(n=n), horodatage)

        browser.close()

    return offres
