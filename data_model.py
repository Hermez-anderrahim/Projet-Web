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
    #Inscrit un nouvel utilisateur en sécurisant son mot de passe.
    
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
    #Vérifie le nom d'utilisateur et compare le mot de passe avec le hachage.
    
    # On cherche l'utilisateur UNIQUEMENT par son nom dans la base
    query = "SELECT id, mot_de_passe, est_parrain FROM utilisateur WHERE nom_utilisateur = ?"
    
    user = db_fetch(query, (nom_utilisateur,), fetch_all=False)

    if user and check_password_hash(user['mot_de_passe'], mot_de_passe):
        return {'id': user['id'], 'est_parrain': user['est_parrain']}
    else:
        return -1


# ── Demandes d'aide ────────────────────────────────────────
def obtenir_demandes():
    #Retourne toutes les demandes d'aide avec le nom et l'id de leur auteur.
    query = """
        SELECT demande_aide.id, demande_aide.matiere, demande_aide.description,
               demande_aide.statut, demande_aide.auteur_id,
               utilisateur.nom_utilisateur AS auteur
        FROM demande_aide
        JOIN utilisateur ON demande_aide.auteur_id = utilisateur.id
        ORDER BY demande_aide.id DESC
    """
    return db_fetch(query, fetch_all=True)


def obtenir_matieres():
    """Retourne la liste des matières distinctes présentes dans les demandes et les ressources."""
    query = """
        SELECT DISTINCT matiere FROM demande_aide
        UNION
        SELECT DISTINCT matiere FROM ressource
        ORDER BY matiere
    """
    rows = db_fetch(query, fetch_all=True)
    return [row['matiere'] for row in rows]


def chercher_demandes(q='', matiere=''):
    """Retourne les demandes filtrées par matière et/ou recherche textuelle."""
    conditions, args = [], []

    if matiere:
        conditions.append("demande_aide.matiere = ?")
        args.append(matiere)

    if q:
        terme = f"%{q.lower()}%"
        conditions.append("(LOWER(demande_aide.matiere) LIKE ? OR LOWER(demande_aide.description) LIKE ?)")
        args += [terme, terme]

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT demande_aide.id, demande_aide.matiere, demande_aide.description,
               demande_aide.statut, demande_aide.auteur_id,
               utilisateur.nom_utilisateur AS auteur
        FROM demande_aide
        JOIN utilisateur ON demande_aide.auteur_id = utilisateur.id
        {where}
        ORDER BY demande_aide.id DESC
    """
    return db_fetch(query, args, fetch_all=True)


def get_demande(demande_id):
    #Retourne une demande d'aide par son identifiant.
    query = """
        SELECT demande_aide.id, demande_aide.matiere, demande_aide.description,
               demande_aide.statut, demande_aide.auteur_id,
               utilisateur.nom_utilisateur AS auteur
        FROM demande_aide
        JOIN utilisateur ON demande_aide.auteur_id = utilisateur.id
        WHERE demande_aide.id = ?
    """
    return db_fetch(query, (demande_id,))


def creer_demande(auteur_id, matiere, description):
    #Crée une nouvelle demande d'aide.
    query = "INSERT INTO demande_aide (auteur_id, matiere, description) VALUES (?, ?, ?)"
    return db_insert(query, (auteur_id, matiere, description))


def cloturer_demande(demande_id, auteur_id):
    #Clôture une demande d'aide si l'utilisateur en est l'auteur.
    query = "UPDATE demande_aide SET statut = 'close' WHERE id = ? AND auteur_id = ?"
    db_update(query, (demande_id, auteur_id))


# ── Réponses ──────────────────────────────────────────────

def get_reponses(demande_id):
    #Retourne toutes les réponses liées à une demande.
    query = """
        SELECT reponse.id, reponse.message, reponse.auteur_id,
               utilisateur.nom_utilisateur AS auteur
        FROM reponse
        JOIN utilisateur ON reponse.auteur_id = utilisateur.id
        WHERE reponse.demande_id = ?
        ORDER BY reponse.id ASC
    """
    return db_fetch(query, (demande_id,), fetch_all=True)


def creer_reponse(demande_id, auteur_id, message):
    #Ajoute une réponse à une demande d'aide.
    query = "INSERT INTO reponse (demande_id, auteur_id, message) VALUES (?, ?, ?)"
    return db_insert(query, (demande_id, auteur_id, message))


def get_reponses_de(user_id):
    #Retourne toutes les réponses d'un utilisateur avec la question associée.
    query = """
        SELECT reponse.id, reponse.message,
               demande_aide.id        AS demande_id,
               demande_aide.matiere,
               demande_aide.description AS question
        FROM reponse
        JOIN demande_aide ON reponse.demande_id = demande_aide.id
        WHERE reponse.auteur_id = ?
        ORDER BY reponse.id DESC
    """
    return db_fetch(query, (user_id,), fetch_all=True)


# ── Ressources ────────────────────────────────────────────

def obtenir_ressources():
    #Retourne toutes les ressources avec le nom et l'id de leur auteur.
    query = """
        SELECT ressource.id, ressource.matiere, ressource.titre, ressource.lien_url,
               ressource.auteur_id, utilisateur.nom_utilisateur AS auteur
        FROM ressource
        JOIN utilisateur ON ressource.auteur_id = utilisateur.id
        ORDER BY ressource.id DESC
    """
    return db_fetch(query, fetch_all=True)


def ajouter_ressource(auteur_id, matiere, titre, lien_url):
    #Ajoute une nouvelle ressource partagée.
    query = "INSERT INTO ressource (auteur_id, matiere, titre, lien_url) VALUES (?, ?, ?, ?)"
    return db_insert(query, (auteur_id, matiere, titre, lien_url))


# ── Parrainage ────────────────────────────────────────────

def creer_parrainage(parrain_id, filleul_id):
    #Crée un lien de parrainage entre un parrain et un filleul.
    query = "INSERT INTO parrainage (parrain_id, filleul_id) VALUES (?, ?)"
    return db_insert(query, (parrain_id, filleul_id))


def obtenir_parrain_de(filleul_id):
    #Retourne le parrain d'un filleul, ou None s'il n'en a pas.
    query = """
        SELECT utilisateur.id, utilisateur.nom_utilisateur
        FROM parrainage
        JOIN utilisateur ON parrainage.parrain_id = utilisateur.id
        WHERE parrainage.filleul_id = ?
    """
    return db_fetch(query, (filleul_id,))


def obtenir_filleuls_de(parrain_id):
    #Retourne la liste des filleuls d'un parrain.
    query = """
        SELECT utilisateur.id, utilisateur.nom_utilisateur
        FROM parrainage
        JOIN utilisateur ON parrainage.filleul_id = utilisateur.id
        WHERE parrainage.parrain_id = ?
    """
    return db_fetch(query, (parrain_id,), fetch_all=True)


# ── Profil utilisateur ───────────────────────────────────

def get_utilisateur(user_id):
    #Retourne les informations publiques d'un utilisateur.
    query = "SELECT id, nom_utilisateur, est_parrain FROM utilisateur WHERE id = ?"
    return db_fetch(query, (user_id,))


def get_stats_utilisateur(user_id):
    #Retourne les compteurs d'activité d'un utilisateur.
    demandes   = db_fetch("SELECT COUNT(*) AS c FROM demande_aide WHERE auteur_id = ?", (user_id,))
    reponses   = db_fetch("SELECT COUNT(*) AS c FROM reponse      WHERE auteur_id = ?", (user_id,))
    ressources = db_fetch("SELECT COUNT(*) AS c FROM ressource     WHERE auteur_id = ?", (user_id,))
    return {
        'demandes':   demandes['c']   if demandes   else 0,
        'reponses':   reponses['c']   if reponses   else 0,
        'ressources': ressources['c'] if ressources else 0,
    }


def obtenir_demandes_de(user_id):
    #Retourne les demandes d'aide créées par un utilisateur.
    query = """
        SELECT id, matiere, description, statut
        FROM demande_aide
        WHERE auteur_id = ?
        ORDER BY id DESC
    """
    return db_fetch(query, (user_id,), fetch_all=True)


def get_parrain_disponible(filleul_id):
    """
    Retourne le parrain disponible ayant le moins de filleuls,
    en excluant ceux qui parrainent déjà cet utilisateur.
    """
    query = """
        SELECT utilisateur.id, utilisateur.nom_utilisateur,
               COUNT(parrainage.filleul_id) AS nb_filleuls
        FROM utilisateur
        LEFT JOIN parrainage ON utilisateur.id = parrainage.parrain_id
        WHERE utilisateur.est_parrain = 1
          AND utilisateur.id NOT IN (
              SELECT parrain_id FROM parrainage WHERE filleul_id = ?
          )
        GROUP BY utilisateur.id
        ORDER BY nb_filleuls ASC
        LIMIT 1
    """
    return db_fetch(query, (filleul_id,))

def valider_mot_de_passe(mdp):
    #Vérifie les 4 critères de sécurité du mot de passe.
    if len(mdp) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."
    if not any(c.isupper() for c in mdp):
        return False, "Le mot de passe doit contenir au moins une lettre majuscule."
    if not any(c.isdigit() for c in mdp):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    if not any(not c.isalnum() for c in mdp):
        return False, "Le mot de passe doit contenir au moins un caractère spécial."
    return True, "Mot de passe valide."

def creer_demande_parrainage(filleul_id, parrain_id, message=""):
    #L'étudiant L1 envoie une demande à un parrain.
    db_insert(
        "INSERT INTO demande_parrainage (filleul_id, parrain_id, message, statut) VALUES (?, ?, ?, 'en_attente')",
        (filleul_id, parrain_id, message)
    )

def obtenir_demandes_parrainage_recues(parrain_id):
    #Retourne les demandes en attente reçues par un parrain.
    return db_fetch(
        """SELECT dp.id, dp.message, dp.statut, dp.created_at,
                  u.id as filleul_id, u.nom_utilisateur
           FROM demande_parrainage dp
           JOIN utilisateur u ON u.id = dp.filleul_id
           WHERE dp.parrain_id = ? AND dp.statut = 'en_attente'
           ORDER BY dp.created_at DESC""",
        (parrain_id,),
        fetch_all=True
    )

def obtenir_parrains_disponibles(filleul_id):
    #Retourne les parrains disponibles
    return db_fetch(
        """SELECT u.id, u.nom_utilisateur,
                  COUNT(p.filleul_id) as nb_filleuls
           FROM utilisateur u
           LEFT JOIN parrainage p ON p.parrain_id = u.id
           WHERE u.est_parrain = 1
             AND u.id NOT IN (
                 SELECT parrain_id FROM parrainage WHERE filleul_id = ?
             )
             AND u.id NOT IN (
                 SELECT parrain_id FROM demande_parrainage
                 WHERE filleul_id = ? AND statut = 'en_attente'
             )
           GROUP BY u.id
           ORDER BY nb_filleuls ASC""",
        (filleul_id, filleul_id),
        fetch_all=True
    )

def repondre_demande_parrainage(demande_id, parrain_id, accepter):
    #Le parrain accepte ou refuse une demande.
    if accepter:
        demande = db_fetch(
            "SELECT filleul_id FROM demande_parrainage WHERE id = ? AND parrain_id = ?",
            (demande_id, parrain_id)
        )
        if demande:
            creer_parrainage(parrain_id, demande['filleul_id'])
            db_run(
                "UPDATE demande_parrainage SET statut = 'acceptee' WHERE id = ?",
                (demande_id,)
            )
    else:
        db_run(
            "UPDATE demande_parrainage SET statut = 'refusee' WHERE id = ?",
            (demande_id,)
        )