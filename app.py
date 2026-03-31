from flask import Flask, render_template, request, redirect, url_for, session
from data_model import (
    login_required,
    inscrire_utilisateur,
    authentifier_utilisateur,
    obtenir_demandes,
    creer_demande,
    cloturer_demande,
    creer_parrainage,
    obtenir_parrain_de,
    obtenir_filleuls_de,
    ajouter_ressource,
    obtenir_ressources,
    get_demande,
    get_reponses,
    creer_reponse,
    get_parrain_disponible,
    get_utilisateur,
    get_stats_utilisateur,
    obtenir_demandes_de,
    get_reponses_de,
)
from create_db import init_db

app = Flask(__name__)
app.secret_key = 'luminy-secret-key'


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
    user_id = inscrire_utilisateur(nom, mdp, est_parrain)
    if user_id == -1:
        return render_template('connexion.html', erreur="Ce nom d'utilisateur est déjà pris.")
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
    demandes = obtenir_demandes()
    return render_template('accueil.html', demandes=demandes)



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
    ajouter_ressource(
        session['user_id'],
        request.form['matiere'],
        request.form['titre'],
        request.form['lien_url']
    )
    return redirect(url_for('ressources'))


# ── Parrainage ─────────────────────────────────────────────
@app.route('/mon-parrainage')
@login_required
def mon_parrainage():
    if session['est_parrain']:
        filleuls = obtenir_filleuls_de(session['user_id'])
        return render_template('parrainage.html', filleuls=filleuls, est_parrain=True)
    else:
        parrain = obtenir_parrain_de(session['user_id'])
        return render_template('parrainage.html', parrain=parrain, est_parrain=False)

@app.route('/demander-parrain', methods=['POST'])
@login_required
def demander_parrain():
    parrain = get_parrain_disponible(session['user_id'])
    if parrain:
        creer_parrainage(parrain['id'], session['user_id'])
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
    init_db()
    app.run(debug=True)