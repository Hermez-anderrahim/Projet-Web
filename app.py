import io

from flask import Flask, render_template, request, redirect, url_for, session, send_file, abort
from werkzeug.utils import secure_filename

from data_model import (
    login_required,
    inscrire_utilisateur,
    authentifier_utilisateur,
    obtenir_demandes,
    obtenir_matieres,
    chercher_demandes,
    creer_demande,
    cloturer_demande,
    creer_parrainage,
    obtenir_parrain_de,
    obtenir_filleuls_de,
    ajouter_ressource,
    obtenir_ressources,
    get_ressource_piece_jointe,
    get_demande,
    get_reponses,
    creer_reponse,
    get_parrain_disponible,
    get_utilisateur,
    get_stats_utilisateur,
    obtenir_demandes_de,
    get_reponses_de,
    valider_mot_de_passe,
     creer_demande_parrainage,
    obtenir_demandes_parrainage_recues,
    obtenir_parrains_disponibles,
    repondre_demande_parrainage,
)
from create_db import init_db

app = Flask(__name__)
app.secret_key = 'luminy-secret-key'

ALLOWED_EXTENSIONS_RESSOURCE = frozenset(
    {"pdf", "png", "jpg", "jpeg", "gif", "webp", "txt", "doc", "docx", "zip", "odt", "ppt", "pptx"}
)

init_db()


def _extension_fichier_autorisee(filename):
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS_RESSOURCE


# ── Auth ───────────────────────────────────────────────────
@app.route('/connexion', methods=['GET'])
def connexion():
    if 'user_id' in session:
        return redirect(url_for('accueil'))
    return render_template('connexion.html', erreur=None)

@app.route('/connexion', methods=['POST'])
def connexion_post():
    nom = request.form['nom_utilisateur']
    mdp = request.form['mot_de_passe']
    user = authentifier_utilisateur(nom, mdp)
    if user == -1:
        return render_template('connexion.html', erreur="Identifiants incorrects.")
    session['user_id']     = user['id']
    session['est_parrain'] = user['est_parrain'] == 1
    session['nom']         = nom
    return redirect(url_for('accueil'))

@app.route('/inscription', methods=['POST'])
def inscription():
    nom         = request.form['nom_utilisateur']
    mdp         = request.form['mot_de_passe']
    est_parrain = 1 if request.form.get('est_parrain') == '1' else 0

    # --- 1. On vérifie la solidité du mot de passe ---
    est_valide, message_erreur = valider_mot_de_passe(mdp)
    
    if not est_valide:
        # Si c'est invalide, on recharge la page avec le message d'erreur approprié
        return render_template('connexion.html', erreur=message_erreur, active_tab='inscription')   
    # --- 2. Si le mot de passe est bon, on continue l'inscription ---
    user_id = inscrire_utilisateur(nom, mdp, est_parrain)
    
    if user_id == -1:
        return render_template('connexion.html', erreur="Ce nom d'utilisateur est déjà pris.", active_tab='inscription')        
    session['user_id']     = user_id
    session['est_parrain'] = est_parrain == 1
    session['nom']         = nom
    
    return redirect(url_for('accueil'))

@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('connexion'))


# ── Accueil ────────────────────────────────────────────────
@app.route('/')
@login_required
def accueil():
    q       = request.args.get('q', '').strip()
    matiere = request.args.get('matiere', '').strip()
    matieres = obtenir_matieres()
    demandes = chercher_demandes(q=q, matiere=matiere) if (q or matiere) else obtenir_demandes()
    return render_template(
        'accueil.html',
        demandes=demandes,
        matieres=matieres,
        q=q,
        matiere_active=matiere,
    )



@app.route('/nouvelle-demande', methods=['GET'])
@login_required
def nouvelle_demande_get():
    return render_template('creer_demande.html')

@app.route('/nouvelle-demande', methods=['POST'])
@login_required
def nouvelle_demande_post():
    creer_demande(session['user_id'], request.form['matiere'], request.form['description'])
    return redirect(url_for('accueil'))

@app.route('/demande/<int:demande_id>')
@login_required
def detail_demande(demande_id):
    demande  = get_demande(demande_id)
    reponses = get_reponses(demande_id)
    return render_template('detail_demande.html', demande=demande, reponses=reponses)

@app.route('/demande/<int:demande_id>/repondre', methods=['POST'])
@login_required
def repondre(demande_id):
    creer_reponse(demande_id, session['user_id'], request.form['message'])
    return redirect(url_for('detail_demande', demande_id=demande_id))

@app.route('/demande/<int:demande_id>/cloturer', methods=['POST'])
@login_required
def cloturer(demande_id):
    cloturer_demande(demande_id, session['user_id'])
    return redirect(url_for('detail_demande', demande_id=demande_id))


# ── Ressources ─────────────────────────────────────────────
@app.route('/ressources')
@login_required
def ressources():
    return render_template('ressources.html', ressources=obtenir_ressources())

@app.route('/ajouter-ressource', methods=['GET'])
@login_required
def ajouter_ressource_get():
    return render_template('ajouter_ressource.html')

@app.route('/ajouter-ressource', methods=['POST'])
@login_required
def ajouter_ressource_post():
    matiere = request.form.get("matiere", "").strip()
    titre = request.form.get("titre", "").strip()
    lien_url = (request.form.get("lien_url") or "").strip()
    fichier = request.files.get("fichier")

    fichier_bytes = None
    fichier_nom_original = None
    if fichier and fichier.filename:
        if not _extension_fichier_autorisee(fichier.filename):
            return render_template(
                "ajouter_ressource.html",
                erreur="Type de fichier non autorisé. Extensions acceptées : "
                + ", ".join(sorted(ALLOWED_EXTENSIONS_RESSOURCE)),
            )
        nom_safe = secure_filename(fichier.filename)
        if not nom_safe:
            return render_template(
                "ajouter_ressource.html",
                erreur="Nom de fichier invalide.",
            )
        fichier_bytes = fichier.read()
        if not fichier_bytes:
            return render_template(
                "ajouter_ressource.html",
                erreur="Le fichier est vide.",
            )
        fichier_nom_original = nom_safe

    if not lien_url and not fichier_bytes:
        return render_template(
            "ajouter_ressource.html",
            erreur="Indiquez au moins un lien URL ou un fichier à joindre.",
        )

    ajouter_ressource(
        session["user_id"],
        matiere,
        titre,
        lien_url,
        fichier_bytes=fichier_bytes,
        fichier_nom_original=fichier_nom_original,
    )
    return redirect(url_for("ressources"))


@app.route("/ressources/fichier/<int:ressource_id>")
@login_required
def telecharger_ressource(ressource_id):
    r = get_ressource_piece_jointe(ressource_id)
    if not r or not r.get("fichier_donnees"):
        abort(404)
    nom = r.get("fichier_nom_original") or "document"
    buf = io.BytesIO(r["fichier_donnees"])
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=nom)


# ── Parrainage ─────────────────────────────────────────────
@app.route('/mon-parrainage')
@login_required
def mon_parrainage():
    if session['est_parrain']:
        filleuls  = obtenir_filleuls_de(session['user_id'])
        demandes  = obtenir_demandes_parrainage_recues(session['user_id'])
        return render_template('parrainage.html',
                               filleuls=filleuls,
                               demandes_recues=demandes,
                               est_parrain=True)
    else:
        parrain  = obtenir_parrain_de(session['user_id'])
        parrains = obtenir_parrains_disponibles(session['user_id']) if not parrain else []        
        return render_template('parrainage.html',
                               parrain=parrain,
                               parrains=parrains,
                               est_parrain=False)

@app.route('/demander-parrain/<int:parrain_id>', methods=['POST'])
@login_required
def demander_parrain_specifique(parrain_id):
    message = request.form.get('message', '')
    creer_demande_parrainage(session['user_id'], parrain_id, message)
    return redirect(url_for('mon_parrainage'))

@app.route('/parrainage/repondre/<int:demande_id>', methods=['POST'])
@login_required
def repondre_parrainage(demande_id):
    accepter = request.form.get('action') == 'accepter'
    repondre_demande_parrainage(demande_id, session['user_id'], accepter)
    return redirect(url_for('mon_parrainage'))


# ── Profil ─────────────────────────────────────────────────
@app.route('/profil')
@login_required
def profil():
    user     = get_utilisateur(session['user_id'])
    stats    = get_stats_utilisateur(session['user_id'])
    demandes = obtenir_demandes_de(session['user_id'])
    return render_template('profil.html', user=user, stats=stats, demandes=demandes)


# ── Profil public ──────────────────────────────────────────
@app.route('/utilisateur/<int:user_id>')
@login_required
def profil_public(user_id):
    user     = get_utilisateur(user_id)
    if not user:
        return redirect(url_for('accueil'))
    stats    = get_stats_utilisateur(user_id)
    reponses = get_reponses_de(user_id)
    return render_template('profil_public.html', user=user, stats=stats, reponses=reponses)


# ── Lancement ──────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)