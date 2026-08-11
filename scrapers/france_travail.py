from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from scrapers.utils import USER_AGENT, accepter_cookies, nettoyer

NOM_SOURCE = "France Travail"

# lieux=17299 est le code interne "commune" de France Travail pour Rochefort
# (different du code postal 17300). rayon=0 = "lieu exact", pas de communes voisines.
URL_ROCHEFORT = "https://candidat.francetravail.fr/offres/recherche?lieux=17299&offresPartenaires=true&rayon=0&tri=0"


def scraper():
    """Récupère les offres visibles sur la 1re page de résultats (les plus récentes,
    tri=0 = tri par date). Suffisant pour une veille qui repasse plusieurs fois par jour."""
    offres = []
    horodatage = datetime.now(timezone.utc).isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(URL_ROCHEFORT, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        accepter_cookies(page)

        cartes = page.locator("li[data-id-offre]")
        nb = cartes.count()

        for i in range(nb):
            carte = cartes.nth(i)
            id_offre = carte.get_attribute("data-id-offre")

            titre = nettoyer(carte.locator(".media-heading-title").inner_text())

            sous_texte = carte.locator("p.subtext").first.inner_text()
            entreprise, _, lieu = sous_texte.partition("\xa0-\xa0")
            entreprise = nettoyer(entreprise)
            lieu = nettoyer(lieu)

            try:
                contrat_bloc = carte.locator("p.contrat:not(.visible-xs)").first.inner_text()
            except Exception:
                contrat_bloc = ""
            contrat, _, temps_travail = contrat_bloc.partition("\n")
            contrat = nettoyer(contrat)
            temps_travail = nettoyer(temps_travail)

            try:
                description = nettoyer(carte.locator("p.description").first.inner_text())
            except Exception:
                description = ""

            try:
                date_pub = nettoyer(carte.locator("p.date").first.inner_text())
            except Exception:
                date_pub = ""

            offres.append({
                "id_offre": id_offre,
                "source": NOM_SOURCE,
                "titre": titre,
                "entreprise": entreprise.strip(),
                "lieu": lieu.strip(),
                "contrat": contrat.strip(),
                "temps_travail": temps_travail.strip(),
                "description": description,
                "date_publication": date_pub,
                "url": f"https://candidat.francetravail.fr/offres/recherche/detail/{id_offre}",
                "date_scraping": horodatage,
            })

        browser.close()

    return offres
