const express = require('express');
const mustacheExpress = require('mustache-express');
const session = require('express-session');
const { db_fetch, db_insert } = require('./database');


const app = express();


app.engine('mustache', mustacheExpress());
app.set('view engine', 'mustache');
app.set('views', __dirname + '/views');


app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));
app.use(session({
    secret: 'luminy_secret_key',
    resave: false,
    saveUninitialized: true
}));

app.use((req, res, next) => {
    res.locals.user = req.session.user || null;
    next();
});

app.get('/', async (req, res) => {

    
    const query = `
        SELECT d.*, u.nom_utilisateur 
        FROM demande_aide d 
        JOIN utilisateur u ON d.auteur_id = u.id 
        WHERE d.statut = 'ouverte' ORDER BY d.id DESC`;
    
    const demandes = await db_fetch(query, [], true);
    res.render('accueil', { demandes });
});

app.get('/demande/:id', async (req, res) => {
    const demande = await db_fetch("SELECT d.*, u.nom_utilisateur FROM demande_aide d JOIN utilisateur u ON d.auteur_id = u.id WHERE d.id = ?", [req.params.id]);
    const reponses = await db_fetch("SELECT r.*, u.nom_utilisateur FROM reponse r JOIN utilisateur u ON r.auteur_id = u.id WHERE r.demande_id = ?", [req.params.id], true);
    res.render('detail_demande', { demande, reponses });
});

app.post('/nouvelle-demande', async (req, res) => {
    const { matiere, description } = req.body;
    await db_insert(
        "INSERT INTO demande_aide (auteur_id, matiere, description) VALUES (?, ?, ?)",
        [req.session.user.id, matiere, description]
    );
    res.redirect('/');
});



app.get('/ressources', async (req, res) => {
    const ressources = await db_fetch(`
        SELECT r.*, u.nom_utilisateur 
        FROM ressource r 
        JOIN utilisateur u ON r.auteur_id = u.id 
        ORDER BY matiere ASC`, [], true);
    res.render('ressources', { ressources });
});
app.get('/nouvelle-demande', (req, res) => {
    res.render('creer_demande');
});

app.post('/ajouter-ressource', async (req, res) => {
    const { matiere, titre, lien } = req.body;
    await db_insert(
        "INSERT INTO ressource (auteur_id, matiere, titre, lien_url) VALUES (?, ?, ?, ?)",
        [req.session.user.id, matiere, titre, lien]
    );
    res.redirect('/ressources');
});

app.listen(3000, () => console.log('Serveur : http://localhost:3000'));