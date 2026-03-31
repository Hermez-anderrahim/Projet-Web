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
    
def obtenir_demandes():
    #Retourne toutes les demandes ouvertes avec le nom de l'auteur.
    query = """
        SELECT d.id, d.matiere, d.description, d.statut, d.auteur_id,
               u.nom_utilisateur AS auteur
        FROM demande_aide d
        JOIN utilisateur u ON d.auteur_id = u.id
        WHERE d.statut = 'ouverte'
        ORDER BY d.id DESC
    """
    return db_fetch(query, fetch_all=True)


def creer_demande(auteur_id, matiere, description):
    #Insère une nouvelle demande d'aide avec le statut 'ouverte' par défaut.
    query = """
        INSERT INTO demande_aide (auteur_id, matiere, description)
        VALUES (?, ?, ?)
    """
    return db_insert(query, (auteur_id, matiere, description))


def cloturer_demande(demande_id, auteur_id):
    #Passe le statut à 'résolue', uniquement si l'auteur correspond.
    query = """
        UPDATE demande_aide
        SET statut = 'résolue'
        WHERE id = ? AND auteur_id = ?
    """
    lignes_modifiees = db_update(query, (demande_id, auteur_id))
    return lignes_modifiees > 0


def get_demande(demande_id):
    #Retourne une demande précise avec le nom de son auteur.
    query = """
        SELECT d.id, d.matiere, d.description, d.statut, d.auteur_id,
               u.nom_utilisateur AS auteur
        FROM demande_aide d
        JOIN utilisateur u ON d.auteur_id = u.id
        WHERE d.id = ?
    """
    return db_fetch(query, (demande_id,))


def get_reponses(demande_id):
    #Retourne toutes les réponses d'une demande avec le nom de leur auteur.
    query = """
        SELECT r.id, r.message, r.auteur_id,
               u.nom_utilisateur AS auteur
        FROM reponse r
        JOIN utilisateur u ON r.auteur_id = u.id
        WHERE r.demande_id = ?
        ORDER BY r.id ASC
    """
    return db_fetch(query, (demande_id,), fetch_all=True)


def creer_reponse(demande_id, auteur_id, message):
    #Insère une nouvelle réponse dans le fil de discussion.
    query = """
        INSERT INTO reponse (demande_id, auteur_id, message)
        VALUES (?, ?, ?)
    """
    return db_insert(query, (demande_id, auteur_id, message))