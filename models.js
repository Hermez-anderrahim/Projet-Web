const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./luminy_connect.sqlite');

function inscrire_utilisateur(nom_utilisateur, mot_de_passe, est_parrain) {
    return new Promise((resolve, reject) => {

        const query = `INSERT INTO utilisateur (nom_utilisateur, mot_de_passe, est_parrain) VALUES (?, ?, ?)`;
        
    
        db.run(query, [nom_utilisateur, mot_de_passe, est_parrain], function(err) {
            if (err) {
                // Si l'erreur est liée à la contrainte UNIQUE (le nom existe déjà)
                if (err.message.includes('UNIQUE constraint failed')) {
                    resolve(-1); // On retourne -1 comme demandé [cite: 35]
                } else {
                    reject(err); // Pour toute autre erreur technique grave
                }
            } else {
                // Succès : on retourne l'ID du nouvel utilisateur [cite: 35]
                resolve(this.lastID);
            }
        });
    });
}

function authentifier_utilisateur(nom_utilisateur, mot_de_passe) {
    return new Promise((resolve, reject) => {
        const query = `SELECT id, est_parrain FROM utilisateur WHERE nom_utilisateur = ? AND mot_de_passe = ?`;
        
        db.get(query, [nom_utilisateur, mot_de_passe], (err, row) => {
            if (err) {
                reject(err);
            } else if (row) {
                // Si row existe, les identifiants sont corrects. 
                // On retourne l'objet contenant l'id et le statut [cite: 38]
                resolve({ id: row.id, est_parrain: row.est_parrain });
            } else {
                // Si row n'existe pas (undefined), les identifiants sont faux.
                // On retourne -1 comme demandé [cite: 38]
                resolve(-1);
            }
        });
    });
}
//on exporte les fonctions utilitaires 
module.exports = {
    inscrire_utilisateur,
    authentifier_utilisateur
};