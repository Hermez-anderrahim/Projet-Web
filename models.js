const { db_fetch, db_insert } = require('./database');


async function inscrire_utilisateur(nom_utilisateur, mot_de_passe, est_parrain) {
    const query = `INSERT INTO utilisateur (nom_utilisateur, mot_de_passe, est_parrain) VALUES (?, ?, ?)`;
    
    try {
        const id = await db_insert(query, [nom_utilisateur, mot_de_passe, est_parrain]);
        return id; 
    } catch (err) {
        if (err.message.includes('UNIQUE')) {
            return -1; // Le nom est déjà pris
        }
        return -1;
    }
}

async function authentifier_utilisateur(nom_utilisateur, mot_de_passe) {
    const query = `SELECT id, est_parrain FROM utilisateur WHERE nom_utilisateur = ? AND mot_de_passe = ?`;
    
    const user = await db_fetch(query, [nom_utilisateur, mot_de_passe], false);
    
    if (user) {
        return { id: user.id, est_parrain: user.est_parrain };
    } else {
        return -1; // Mauvais id
    }
}

module.exports = { inscrire_utilisateur, authentifier_utilisateur };