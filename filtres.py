"""Classification des offres par mots-clés du titre.

Aucun site (France Travail, Hellowork, Rochefort Emplois) n'expose de vrai filtre
"sans qualification" en API : on approxime donc à partir du titre. Ces listes sont
volontairement modifiables à la main si des faux positifs/négatifs apparaissent.
"""

MOTS_ALTERNANCE = [
    "alternance",
    "apprentissage",
    "apprenti",
    "contrat pro",
    "contrat de professionnalisation",
]

MOTS_QUALIFIES = [
    # ingénierie / technique de haut niveau
    "ingénieur", "ingenieur", "ingénierie", "ingenierie",
    "bureau d'études", "bureau d etudes",
    "architecte", "urbaniste",
    "data scientist", "développeur", "developpeur", "devops",
    # encadrement / gestion
    "chef de projet", "chef de chantier", "chef d'équipe", "chef d equipe",
    "responsable", "directeur", "directrice", "manager", "cadre",
    "consultant", "chargé d'affaires", "charge d affaires",
    # professions réglementées / diplôme obligatoire
    "infirmier", "infirmière", "infirmiere", "médecin", "medecin",
    "pharmacien", "kinésithérapeute", "kinesitherapeute", "psychologue",
    "avocat", "notaire", "expert-comptable", "comptable", "juriste",
    "professeur", "enseignant", "formateur",
    # séniorité explicite
    "senior", "confirmé", "confirme", "expert(e)",
]

# Métiers manuels/techniques qui demandent généralement un CAP/BEP/Bac Pro ou un
# permis spécifique (BTP, industrie, conduite) — distincts des postes "cadre" ci-dessus.
MOTS_METIERS_TECHNIQUES = [
    # BTP
    "plombier", "maçon", "macon", "électricien", "electricien",
    "peintre", "plaquiste", "carreleur", "charpentier", "couvreur",
    "menuisier", "soudeur", "chaudronnier",
    # industrie / aéronautique
    "tourneur", "fraiseur", "ajusteur", "monteur", "assembleur",
    "intégrateur", "integrateur", "dessinateur", "projeteur",
    "opérateur machine", "operateur machine", "installateur",
    "technicien", "mécanicien", "mecanicien",
    # conduite avec permis/certification
    "chauffeur spl", "chauffeur pl", "conducteur routier",
]


def _contient_un_mot(texte, mots):
    texte_bas = (texte or "").lower()
    return any(mot in texte_bas for mot in mots)


def est_alternance(offre):
    return _contient_un_mot(offre.get("titre"), MOTS_ALTERNANCE) or _contient_un_mot(
        offre.get("contrat"), MOTS_ALTERNANCE
    )


def est_poste_qualifie(offre):
    return _contient_un_mot(offre.get("titre"), MOTS_QUALIFIES)


def est_metier_technique(offre):
    return _contient_un_mot(offre.get("titre"), MOTS_METIERS_TECHNIQUES)
