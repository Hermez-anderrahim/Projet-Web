import sqlite3
from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

DBFILENAME = './luminy_connect.sqlite'

def login_required(f):
    """Vérifie si l'utilisateur est connecté avant d'autoriser l'accès."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('connexion')) 
        return f(*args, **kwargs)
    return decorated_function


def db_fetch(query, args=(), fetch_all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        
        if fetch_all:
            res = cur.fetchall()
            return [dict(e) for e in res] if res else []
        else:
            res = cur.fetchone()
            return dict(res) if res else None

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
    
def inscrire_utilisateur(nom_utilisateur, mot_de_passe, est_parrain):
    """Inscrit un nouvel utilisateur en sécurisant son mot de passe."""
    
    # On transforme le mot de passe
    mot_de_passe_hache = generate_password_hash(mot_de_passe)
    
    # on va insérer le mot de passe haché
    query = "INSERT INTO utilisateur (nom_utilisateur, mot_de_passe, est_parrain) VALUES (?, ?, ?)"
    
    try:
        # On tente l'insertion
        nouvel_id = db_insert(query, (nom_utilisateur, mot_de_passe_hache, est_parrain))
        return nouvel_id
        
    except sqlite3.IntegrityError:
        # le nom_utilisateur existe déjà
        return -1


def authentifier_utilisateur(nom_utilisateur, mot_de_passe):
    """Vérifie le nom d'utilisateur et compare le mot de passe avec le hachage."""
    
    # On cherche l'utilisateur UNIQUEMENT par son nom dans la base
    query = "SELECT id, mot_de_passe, est_parrain FROM utilisateur WHERE nom_utilisateur = ?"
    
    user = db_fetch(query, (nom_utilisateur,), fetch_all=False)

    if user and check_password_hash(user['mot_de_passe'], mot_de_passe):
        # Succès : on renvoie un dictionnaire avec les infos
        return {'id': user['id'], 'est_parrain': user['est_parrain']}
    else:
        # Échec (mauvais nom ou mauvais mot de passe)
        return -1