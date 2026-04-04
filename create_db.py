import sqlite3

# Le nom de ta base de données
DB_FILE = './luminy_connect.sqlite'

def db_run(query, args=(), db_name=DB_FILE):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()

def init_db():
    """Crée toutes les tables si elles n'existent pas déjà."""
    
    # 1. Table utilisateur
    db_run("""
        CREATE TABLE IF NOT EXISTS utilisateur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            est_parrain INTEGER NOT NULL
        )
    """)

    # 2. Table demande_aide
    db_run("""
        CREATE TABLE IF NOT EXISTS demande_aide (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auteur_id INTEGER NOT NULL,
            matiere TEXT NOT NULL,
            description TEXT NOT NULL,
            statut TEXT DEFAULT 'ouverte',
            FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
        )
    """)

    # 3. Table reponse
    db_run("""
        CREATE TABLE IF NOT EXISTS reponse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_id INTEGER NOT NULL,
            auteur_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (demande_id) REFERENCES demande_aide(id),
            FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
        )
    """)

    # 4. Table parrainage
    db_run("""
        CREATE TABLE IF NOT EXISTS parrainage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parrain_id INTEGER NOT NULL,
            filleul_id INTEGER NOT NULL,
            FOREIGN KEY (parrain_id) REFERENCES utilisateur(id),
            FOREIGN KEY (filleul_id) REFERENCES utilisateur(id)
        )
    """)

    # 5. Table ressource
    db_run("""
        CREATE TABLE IF NOT EXISTS ressource (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auteur_id INTEGER NOT NULL,
            matiere TEXT NOT NULL,
            titre TEXT NOT NULL,
            lien_url TEXT NOT NULL DEFAULT '',
            fichier_stocke TEXT,
            fichier_nom_original TEXT,
            fichier_donnees BLOB,
            FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
        )
    """)

    # Migration : ajouter fichier_donnees aux bases créées avant cette colonne
    with sqlite3.connect(DB_FILE) as conn:
        cols = [row[1] for row in conn.execute("PRAGMA table_info(ressource)").fetchall()]
        if cols and "fichier_donnees" not in cols:
            conn.execute("ALTER TABLE ressource ADD COLUMN fichier_donnees BLOB")
            conn.commit()

    # 6. Table demande parrainage
    db_run("""
    CREATE TABLE IF NOT EXISTS demande_parrainage (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        filleul_id INTEGER NOT NULL REFERENCES utilisateur(id),
        parrain_id INTEGER NOT NULL REFERENCES utilisateur(id),
        message    TEXT    DEFAULT '',
        statut     TEXT    DEFAULT 'en_attente',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
if __name__ == '__main__':
    init_db()