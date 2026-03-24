const express = require('express');
const mustacheExpress = require('mustache-express');
const DB = require('./database'); 
const app = express();
const { inscrire_utilisateur, authentifier_utilisateur } = require('./models');

app.engine('mustache', mustacheExpress());
app.set('view engine', 'mustache');
app.set('views', __dirname + '/views');
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

app.use((req, res, next) => {
    // On simule un utilisateur existant dans votre table (ex: ID 1)
    res.locals.user = { id: 1, nom_utilisateur: "Abderrahim", est_parrain: 0 };
    next();
});

// --- ROUTES ---

app.get('/', async (req, res) => {
    try {
        const demandes = await DB.obtenirDemandes();
        res.render('accueil', { demandes });
    } catch (err) {
        res.status(500).send("Erreur base de données : " + err.message);
    }
});

app.get('/demande/:id', async (req, res) => {
    try {
        const demande = await DB.obtenirDemandeParId(req.params.id);
        const reponses = await DB.obtenirReponses(req.params.id);
        res.render('detail_demande', { demande, reponses });
    } catch (err) {
        res.status(404).send("Demande introuvable");
    }
});

app.post('/nouvelle-demande', async (req, res) => {
    const { matiere, description } = req.body;
    await DB.ajouterDemande(res.locals.user.id, matiere, description);
    res.redirect('/');
});

app.post('/demande/:id/repondre', async (req, res) => {
    const { message } = req.body;
    await DB.ajouterReponse(req.params.id, res.locals.user.id, message);
    res.redirect(`/demande/${req.params.id}`);
});

app.get('/ressources', async (req, res) => {
    const ressources = await DB.obtenirRessources();
    res.render('ressources', { ressources });
});

app.listen(3000, () => console.log('Luminy-Connect prêt sur http://localhost:3000'));