import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "offres.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS offres (
            source TEXT NOT NULL,
            id_offre TEXT NOT NULL,
            titre TEXT NOT NULL,
            entreprise TEXT,
            lieu TEXT,
            contrat TEXT,
            temps_travail TEXT,
            description TEXT,
            date_publication TEXT,
            url TEXT NOT NULL,
            date_scraping TEXT NOT NULL,
            PRIMARY KEY (source, id_offre)
        )
    """)
    conn.commit()
    conn.close()


def offre_existe(source, id_offre):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM offres WHERE source = ? AND id_offre = ?", (source, id_offre)
    ).fetchone()
    conn.close()
    return row is not None


def ajouter_offre(offre):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO offres
        (source, id_offre, titre, entreprise, lieu, contrat, temps_travail, description, date_publication, url, date_scraping)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        offre["source"], offre["id_offre"], offre["titre"], offre["entreprise"],
        offre["lieu"], offre["contrat"], offre["temps_travail"], offre["description"],
        offre["date_publication"], offre["url"], offre["date_scraping"],
    ))
    conn.commit()
    conn.close()


def toutes_les_offres():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM offres ORDER BY date_scraping DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
