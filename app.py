from flask import Flask, request, session, redirect, url_for, render_template
from data_model import inscrire_utilisateur, authentifier_utilisateur, login_required

app = Flask(__name__)
app.secret_key = 'une_cle_tres_secrete_pour_luminy'


@app.route('/inscription', methods=['POST'])
def inscription():
    nom = request.form.get('nom_utilisateur')
    mdp = request.form.get('mot_de_passe')
    type_etudiant = request.form.get('type_etudiant')
    
    # 2. Logique spécifique : on convertit le texte du formulaire en 0 ou 1 pour SQLite
    est_parrain = 1 if type_etudiant == 'parrain' else 0

    # 3. Appel de la fonction métier (pas besoin de "await" en Python !)
    resultat = inscrire_utilisateur(nom, mdp, est_parrain)

    # 4. Gestion de la réponse
    if resultat == -1:
        return "Erreur : Ce nom d'utilisateur est déjà pris."
    else:
        # Succès : on connecte l'utilisateur automatiquement en l'ajoutant à la session
        session['user_id'] = resultat
        session['est_parrain'] = est_parrain
        return redirect(url_for('accueil'))


# ==========================================
# 2. ROUTE DE CONNEXION
# ==========================================
# Cette route accepte GET (pour afficher la page) et POST (pour valider le formulaire)
@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    # Si l'utilisateur tape l'URL dans son navigateur (GET)
    if request.method == 'GET':
        return render_template('connexion.html') # Équivalent de res.render() avec Mustache
        
    # Si l'utilisateur a cliqué sur le bouton "Se connecter" (POST)
    elif request.method == 'POST':
        nom = request.form.get('nom_utilisateur')
        mdp = request.form.get('mot_de_passe')

        user = authentifier_utilisateur(nom, mdp)

        if user == -1:
            return "Identifiants incorrects."
        else:
            session['user_id'] = user['id']
            session['est_parrain'] = user['est_parrain']
            return redirect(url_for('accueil'))


# ==========================================
# 3. ROUTE ACCUEIL (Protégée)
# ==========================================
@app.route('/')
@login_required # On utilise le décorateur que tu as créé !
def accueil():
    # Grâce au décorateur, si on arrive ici, on est sûr d'être connecté
    user_id = session.get('user_id')
    statut = "Parrain" if session.get('est_parrain') == 1 else "Filleul"
    
    return f"Bienvenue sur Luminy-Connect ! Tu es le {statut} numéro {user_id}."


if __name__ == '__main__':
    # Équivalent de app.listen(3000)
    app.run(debug=True, port=3000)