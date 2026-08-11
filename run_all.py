import sys
import traceback
from datetime import datetime

from db import init_db, ajouter_offre, offre_existe
from scrapers import france_travail, hellowork, rochefort_emplois

SCRAPERS = [france_travail, hellowork, rochefort_emplois]


def lancer_scraper(module):
    nom = getattr(module, "NOM_SOURCE", module.__name__)
    try:
        offres = module.scraper()
    except Exception:
        print(f"[{nom}] ERREUR pendant le scraping :")
        traceback.print_exc()
        return 0, 0

    nb_nouvelles = sum(1 for o in offres if not offre_existe(o["source"], o["id_offre"]))
    for offre in offres:
        ajouter_offre(offre)

    print(f"[{nom}] {len(offres)} offre(s) vue(s), {nb_nouvelles} nouvelle(s).")
    return len(offres), nb_nouvelles


def main():
    print(f"\n=== Passage du {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    init_db()
    total_vues = 0
    total_nouvelles = 0

    for module in SCRAPERS:
        vues, nouvelles = lancer_scraper(module)
        total_vues += vues
        total_nouvelles += nouvelles

    print(f"\nTotal : {total_vues} offre(s) vue(s), {total_nouvelles} nouvelle(s) ajoutée(s) à offres.db.")


if __name__ == "__main__":
    sys.exit(main())
