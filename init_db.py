"""
init_db.py — Recrée cineflow.db en SQLite natif.
Remplace le dump phpMyAdmin/MariaDB (ENGINE=InnoDB, backticks, ALTER TABLE ADD CONSTRAINT)
par un schéma 100 % compatible SQLite.

Corrections appliquées :
  - "telehone" → "telephone"
  - Contraintes CHECK natives SQLite (prix > 0, note BETWEEN 1 AND 5, capacite > 0)
  - Clés étrangères déclarées dans CREATE TABLE (pas en ALTER TABLE séparé)
  - Table avis peuplée (était vide dans le .db malgré le SQL source)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "cineflow.db")


# ── Schéma SQLite natif ────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS client (
    id_client  INTEGER PRIMARY KEY AUTOINCREMENT,
    nom        TEXT    NOT NULL,
    prenom     TEXT    NOT NULL,
    email      TEXT,
    telephone  TEXT
);

CREATE TABLE IF NOT EXISTS film (
    id_film        INTEGER PRIMARY KEY AUTOINCREMENT,
    titre          TEXT    NOT NULL,
    genre          TEXT,
    date_sortie    TEXT,
    duree_minutes  INTEGER CHECK (duree_minutes > 0),
    realisateur    TEXT
);

CREATE TABLE IF NOT EXISTS salle (
    id_salle   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_salle  TEXT    NOT NULL,
    capacite   INTEGER CHECK (capacite > 0)
);

CREATE TABLE IF NOT EXISTS projection (
    id_projection   INTEGER PRIMARY KEY AUTOINCREMENT,
    date_projection TEXT NOT NULL,
    heure           TEXT NOT NULL,
    id_film         INTEGER NOT NULL REFERENCES film(id_film),
    id_salle        INTEGER NOT NULL REFERENCES salle(id_salle)
);

CREATE TABLE IF NOT EXISTS ticket (
    id_ticket    INTEGER PRIMARY KEY AUTOINCREMENT,
    prix         REAL    CHECK (prix > 0),
    date_achat   TEXT    NOT NULL,
    id_client    INTEGER NOT NULL REFERENCES client(id_client),
    id_projection INTEGER NOT NULL REFERENCES projection(id_projection)
);

CREATE TABLE IF NOT EXISTS avis (
    id_avis     INTEGER PRIMARY KEY AUTOINCREMENT,
    note        INTEGER CHECK (note >= 1 AND note <= 5),
    commentaire TEXT,
    date_avis   TEXT    NOT NULL,
    id_client   INTEGER NOT NULL REFERENCES client(id_client),
    id_film     INTEGER NOT NULL REFERENCES film(id_film)
);
"""

# ── Données ────────────────────────────────────────────────────────────────────

CLIENTS = [
    (1, 'Niang',   'Cheikh',    'cheikh1@mail.com',    '771234567'),
    (2, 'Fall',    'Tidiane',   'tidiane2@mail.com',   '778765432'),
    (3, 'Sow',     'Aminata',   'aminata3@mail.com',   '770111222'),
    (4, 'Ba',      'Mamadou',   'mamadou4@mail.com',   '770222333'),
    (5, 'Diop',    'Fatou',     'fatou5@mail.com',     '770333444'),
    (6, 'Gueye',   'Ousmane',   'ousmane6@mail.com',   '770444555'),
    (7, 'Ndiaye',  'Seynabou',  'seynabou7@mail.com',  '770555666'),
    (8, 'Sy',      'Ibrahima',  'ibrahima8@mail.com',  '770666777'),
    (9, 'Kane',    'Mame',      'mame9@mail.com',      '770777888'),
    (10, 'Faye',   'Lamine',    'lamine10@mail.com',   '770888999'),
    (11, 'Sarr',   'Ndèye',     'ndeye11@mail.com',    '770999000'),
    (12, 'Camara', 'Aliou',     'aliou12@mail.com',    '771000111'),
    (13, 'Barry',  'Mariama',   'mariama13@mail.com',  '771111222'),
    (14, 'Mbaye',  'Khady',     'khady14@mail.com',    '771222333'),
    (15, 'Diagne', 'Serigne',   'serigne15@mail.com',  '771333444'),
    (16, 'Thiam',  'Pape',      'pape16@mail.com',     '771444555'),
    (17, 'Fall',   'Coumba',    'coumba17@mail.com',   '771555666'),
    (18, 'Seck',   'Abdou',     'abdou18@mail.com',    '771666777'),
    (19, 'Niane',  'Aissatou',  'aissatou19@mail.com', '771777888'),
    (20, 'Diallo', 'Boubacar',  'boubacar20@mail.com', '771888999'),
]

FILMS = [
    (1,  'Inception',          'Science-fiction', '2010-07-16', 148, 'Christopher Nolan'),
    (2,  'Titanic',            'Drame',           '1997-12-19', 195, 'James Cameron'),
    (3,  'Avengers: Endgame',  'Action',          '2019-04-26', 181, 'Anthony Russo'),
    (4,  'Interstellar',       'Science-fiction', '2014-11-07', 169, 'Christopher Nolan'),
    (5,  'The Matrix',         'Action',          '1999-03-31', 136, 'Lana Wachowski'),
    (6,  'Joker',              'Drame',           '2019-10-04', 122, 'Todd Phillips'),
    (7,  'Parasite',           'Thriller',        '2019-05-30', 132, 'Bong Joon-ho'),
    (8,  'The Godfather',      'Crime',           '1972-03-24', 175, 'Francis Ford Coppola'),
    (9,  'Pulp Fiction',       'Crime',           '1994-10-14', 154, 'Quentin Tarantino'),
    (10, 'Fight Club',         'Drame',           '1999-10-15', 139, 'David Fincher'),
    (11, 'Forrest Gump',       'Drame',           '1994-07-06', 142, 'Robert Zemeckis'),
    (12, 'The Dark Knight',    'Action',          '2008-07-18', 152, 'Christopher Nolan'),
    (13, 'Gladiator',          'Action',          '2000-05-05', 155, 'Ridley Scott'),
    (14, 'Black Panther',      'Action',          '2018-02-16', 134, 'Ryan Coogler'),
    (15, 'La La Land',         'Musical',         '2016-12-09', 128, 'Damien Chazelle'),
]

SALLES = [
    (1, 'Salle 1', 120),
    (2, 'Salle 2',  80),
    (3, 'Salle 3', 150),
]

PROJECTIONS = [
    (1,  '2025-05-01', '18:00:00',  1, 1),
    (2,  '2025-05-01', '21:00:00',  2, 2),
    (3,  '2025-05-02', '16:00:00',  3, 3),
    (4,  '2025-05-02', '19:30:00',  4, 1),
    (5,  '2025-05-03', '17:00:00',  5, 2),
    (6,  '2025-05-03', '20:00:00',  6, 3),
    (7,  '2025-05-04', '15:00:00',  7, 1),
    (8,  '2025-05-04', '18:30:00',  8, 2),
    (9,  '2025-05-05', '20:00:00',  9, 3),
    (10, '2025-05-05', '14:00:00', 10, 1),
    (11, '2025-05-06', '16:30:00', 11, 2),
    (12, '2025-05-06', '19:00:00', 12, 3),
    (13, '2025-05-07', '21:00:00', 13, 1),
    (14, '2025-05-07', '17:30:00', 14, 2),
    (15, '2025-05-08', '20:00:00', 15, 3),
    (16, '2025-05-08', '18:00:00',  1, 1),
    (17, '2025-05-09', '19:00:00',  2, 2),
    (18, '2025-05-09', '15:00:00',  3, 3),
    (19, '2025-05-10', '17:00:00',  4, 1),
    (20, '2025-05-10', '20:00:00',  5, 2),
]

TICKETS = [
    (1,  3000.00, '2025-04-28',  1,  1),
    (2,  3000.00, '2025-04-28',  1,  2),
    (3,  3500.00, '2025-04-29',  2,  3),
    (4,  3500.00, '2025-04-29',  3,  4),
    (5,  3000.00, '2025-04-30',  4,  5),
    (6,  4000.00, '2025-04-30',  5,  6),
    (7,  4000.00, '2025-05-01',  6,  7),
    (8,  3000.00, '2025-05-01',  7,  8),
    (9,  3500.00, '2025-05-02',  8,  9),
    (10, 3500.00, '2025-05-02',  9, 10),
    (11, 3000.00, '2025-05-03', 10, 11),
    (12, 3000.00, '2025-05-03', 11, 12),
    (13, 4000.00, '2025-05-04', 12, 13),
    (14, 3000.00, '2025-05-04', 13, 14),
    (15, 3500.00, '2025-05-05', 14, 15),
    (16, 3500.00, '2025-05-05', 15, 16),
    (17, 3000.00, '2025-05-06', 16, 17),
    (18, 4000.00, '2025-05-06', 17, 18),
    (19, 3000.00, '2025-05-07', 18, 19),
    (20, 4000.00, '2025-05-07', 19, 20),
    (21, 3000.00, '2025-05-08', 20,  1),
    (22, 3500.00, '2025-05-08',  1,  3),
    (23, 3500.00, '2025-05-08',  2,  3),
    (24, 4000.00, '2025-05-09',  3,  5),
    (25, 4000.00, '2025-05-09',  4,  7),
    (26, 4000.00, '2025-05-09',  5,  9),
    (27, 3500.00, '2025-05-09',  6, 11),
    (28, 3500.00, '2025-05-09',  7, 13),
    (29, 3000.00, '2025-05-09',  8, 15),
    (30, 3000.00, '2025-05-09',  9, 17),
]

AVIS = [
    (1,  5, 'Excellent film !',         '2025-04-28',  1,  1),
    (2,  4, 'Très bon mais un peu long.','2025-04-28',  2,  2),
    (3,  5, "Chef-d'oeuvre !",           '2025-04-29',  3,  3),
    (4,  3, 'Pas à mon goût.',           '2025-04-30',  4,  4),
    (5,  5, 'Très émouvant.',            '2025-04-30',  5,  5),
    (6,  4, 'Bonne histoire.',           '2025-05-01',  6,  6),
    (7,  2, 'Bof, scénario confus.',     '2025-05-02',  7,  7),
    (8,  4, 'Sympa pour un dimanche.',   '2025-05-02',  8,  8),
    (9,  5, 'Mon film préféré !',        '2025-05-03',  9,  9),
    (10, 3, 'Pas mal.',                  '2025-05-04', 10, 10),
]

# ── Construction ───────────────────────────────────────────────────────────────

def build():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[OK] Ancienne base supprimee : {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    cur.executemany(
        "INSERT INTO client VALUES (?,?,?,?,?)", CLIENTS)
    cur.executemany(
        "INSERT INTO film VALUES (?,?,?,?,?,?)", FILMS)
    cur.executemany(
        "INSERT INTO salle VALUES (?,?,?)", SALLES)
    cur.executemany(
        "INSERT INTO projection VALUES (?,?,?,?,?)", PROJECTIONS)
    cur.executemany(
        "INSERT INTO ticket VALUES (?,?,?,?,?)", TICKETS)
    cur.executemany(
        "INSERT INTO avis VALUES (?,?,?,?,?,?)", AVIS)

    con.commit()

    # ── Vérification des comptes ──────────────────────────────────────────────
    counts = {}
    for table in ("client", "film", "salle", "projection", "ticket", "avis"):
        counts[table] = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    # ── Statistiques financières ──────────────────────────────────────────────
    total_revenus = cur.execute("SELECT SUM(prix) FROM ticket").fetchone()[0]
    prix_moyen    = cur.execute("SELECT AVG(prix) FROM ticket").fetchone()[0]

    con.close()

    print("\n=== BASE RECREE — CINEFLOW ===")
    print(f"  Chemin : {DB_PATH}")
    print()
    print("  Enregistrements insérés :")
    for table, n in counts.items():
        print(f"    {table:<12} {n:>3} lignes")
    print()
    print("  Statistiques financières (vérité pour le README) :")
    print(f"    Revenus totaux  : {total_revenus:,.0f} FCFA")
    print(f"    Prix moyen      : {prix_moyen:,.2f} FCFA")
    print()
    print("  Colonnes corrigees : 'telehone' -> 'telephone'")
    print("  Table avis         : peuplee (10 avis, etait vide dans l'ancien .db)")


if __name__ == "__main__":
    build()
