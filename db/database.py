import sqlite3
import json

DBFILENAME = 'luminy_connect.sqlite'

def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row 
        cur = conn.execute(query, args)
        if all:
            res = cur.fetchall()
            if res:
                res = [dict(e) for e in res]
            else:
                res = []
        else:
            res = cur.fetchone()
            if res:
                res = dict(res)
    return res

def db_insert(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid

def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()

def db_update(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount

class LuminyConnectDB:

    def __init__(self, db_path=None):
        #1.table utilisateur
        db_run("""
            CREATE TABLE IF NOT EXISTS utilisateur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL,
                est_parrain INTEGER NOT NULL
            )
        """)

        #2.table demande_aide
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

        #3.table reponse
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
        #4.table parrainage
        db_run("""
            CREATE TABLE IF NOT EXISTS parrainage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parrain_id INTEGER NOT NULL,
                filleul_id INTEGER NOT NULL,
                FOREIGN KEY (parrain_id) REFERENCES utilisateur(id),
                FOREIGN KEY (filleul_id) REFERENCES utilisateur(id)
            )
        """)

        #5.table ressource
        db_run("""
            CREATE TABLE IF NOT EXISTS ressource (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auteur_id INTEGER NOT NULL,
                matiere TEXT NOT NULL,
                titre TEXT NOT NULL,
                lien_url TEXT NOT NULL,
                FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
            )
        """)

        if db_path is not None:
            self.load(db_path)
if __name__ == '__main__':
    db = LuminyConnectDB()
   
    