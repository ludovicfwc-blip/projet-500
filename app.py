import pandas as pd
import streamlit as st

from db import init_db, toutes_les_offres
from filtres import est_alternance, est_metier_technique, est_poste_qualifie

st.set_page_config(page_title="Projet 500 - Offres Rochefort", page_icon="🛴", layout="wide")

init_db()

st.title("🛴 Projet 500 — Veille d'offres à Rochefort-sur-Mer (17300)")
st.caption("Offres à distance de trottinette, mises à jour à chaque passage du scraper.")

offres = toutes_les_offres()

if not offres:
    st.info("Aucune offre en base pour l'instant. Lance `python scraper.py` pour la première collecte.")
    st.stop()

df = pd.DataFrame(offres)
df["contrat"] = df["contrat"].replace("", "Non précisé").fillna("Non précisé")
df["_alternance"] = df.apply(lambda o: est_alternance(o), axis=1)
df["_qualifie"] = df.apply(lambda o: est_poste_qualifie(o), axis=1)
df["_technique"] = df.apply(lambda o: est_metier_technique(o), axis=1)

with st.sidebar:
    st.header("Filtres")
    masquer_alternance = st.checkbox("Masquer les alternances / apprentissage", value=True)
    masquer_qualifie = st.checkbox(
        "Masquer les postes très qualifiés (ingénieur, cadre, infirmier...)", value=True
    )
    masquer_technique = st.checkbox(
        "Masquer les métiers techniques qualifiés (plombier, maçon, électricien...)", value=True
    )
    recherche = st.text_input("Mots-clés (titre, description)", "")
    sources = sorted(df["source"].dropna().unique().tolist())
    sources_choisies = st.multiselect("Source", sources, default=sources)
    contrats = sorted(df["contrat"].dropna().unique().tolist())
    contrats_choisis = st.multiselect("Type de contrat", contrats, default=contrats)

df_filtre = df[df["source"].isin(sources_choisies) & df["contrat"].isin(contrats_choisis)]
if masquer_alternance:
    df_filtre = df_filtre[~df_filtre["_alternance"]]
if masquer_qualifie:
    df_filtre = df_filtre[~df_filtre["_qualifie"]]
if masquer_technique:
    df_filtre = df_filtre[~df_filtre["_technique"]]
if recherche:
    masque = (
        df_filtre["titre"].str.contains(recherche, case=False, na=False)
        | df_filtre["description"].str.contains(recherche, case=False, na=False)
        | df_filtre["entreprise"].str.contains(recherche, case=False, na=False)
    )
    df_filtre = df_filtre[masque]

st.write(f"**{len(df_filtre)}** offre(s) affichée(s) sur **{len(df)}** en base.")

for _, offre in df_filtre.iterrows():
    with st.container(border=True):
        col_gauche, col_droite = st.columns([4, 1])
        with col_gauche:
            st.markdown(f"#### [{offre['titre']}]({offre['url']})")
            st.write(f"**{offre['entreprise']}** — {offre['lieu']}")
            if offre["description"]:
                st.write(offre["description"])
        with col_droite:
            st.write(f"**{offre['contrat']}**")
            if offre["temps_travail"]:
                st.write(offre["temps_travail"])
            if offre["date_publication"]:
                st.caption(offre["date_publication"])
            st.caption(f"via {offre['source']}")
