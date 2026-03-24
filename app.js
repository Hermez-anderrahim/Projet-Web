const express = require('express');
const mustacheExpress = require('mustache-express');
const app = express();

// --- CONFIGURATION ---
app.engine('mustache', mustacheExpress());
app.set('view engine', 'mustache');
app.set('views', __dirname + '/views');
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

// --- LES MOCKS (Fausses données pour tester) ---
let mockUser = { id: 1, nom_utilisateur: "Abderrahim", est_parrain: 0 }; // Change 0 en 1 pour tester le mode Parrain

let mockDemandes = [
    { id: 1, nom_utilisateur: "Alice", matiere: "Algorithmique", description: "C'est quoi l'entropie de Huffman ?", statut: "ouverte" },
    { id: 2, nom_utilisateur: "Bob", matiere: "Web", description: "Problème avec les routes Express", statut: "ouverte" }
];

let mockReponses = [
    { id: 1, demande_id: 1, nom_utilisateur: "ExpertJS", message: "Regarde dans le TP 2 !" }
];

let mockRessources = [
    { id: 1, matiere: "Maths", titre: "Cours Algèbre L2", nom_utilisateur: "Lylia", lien_url: "#" }
];


app.get('/', (req, res) => {
    res.render('accueil', { demandes: mockDemandes, user: mockUser });
});


app.get('/nouvelle-demande', (req, res) => {
    res.render('creer_demande', { user: mockUser });
});


app.post('/nouvelle-demande', (req, res) => {
    console.log("Nouvelle demande reçue :", req.body);
    res.redirect('/');
});

// Détail d'une demande + ses réponses
app.get('/demande/:id', (req, res) => {
    const demande = mockDemandes.find(d => d.id == req.params.id);
    const reponses = mockReponses.filter(r => r.demande_id == req.params.id);
    res.render('detail_demande', { demande, reponses, user: mockUser });
});

// Action : Répondre à une demande
app.post('/demande/:id/repondre', (req, res) => {
    console.log(`Réponse pour la demande ${req.params.id} :`, req.body.message);
    res.redirect(`/demande/${req.params.id}`);
});

// --- ROUTES : RESSOURCES ---

app.get('/ressources', (req, res) => {
    res.render('ressources', { ressources: mockRessources, user: mockUser });
});

app.get('/ajouter-ressource', (req, res) => {
    res.render('ajouter_ressource', { user: mockUser });
});

app.post('/ajouter-ressource', (req, res) => {
    console.log("Ressource ajoutée :", req.body);
    res.redirect('/ressources');
});

// --- ROUTES : PARRAINAGE ---

app.get('/mon-parrainage', (req, res) => {
    // On simule un parrain si l'utilisateur est un filleul (est_parrain: 0)
    const parrain = mockUser.est_parrain === 0 ? { nom_utilisateur: "Jean-L2" } : null;
    const filleuls = mockUser.est_parrain === 1 ? [{ nom_utilisateur: "Petit-Nouveau" }] : [];
    
    res.render('parrainage', { 
        user: mockUser, 
        est_parrain: mockUser.est_parrain === 1,
        parrain: parrain,
        filleuls: filleuls
    });
});

app.listen(3000, () => {
    console.log('Serveur lancé sur http://localhost:3000');
});