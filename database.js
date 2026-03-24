const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./luminy_connect.sqlite');

function db_fetch(query, args = [], fetchAll = false) {
    return new Promise((resolve, reject) => {
        if (fetchAll) {
            // db.all 
            db.all(query, args, (err, rows) => {
                if (err) {
                    reject(err); // On casse la promesse
                } else {
                    resolve(rows); // On valide 
                }
            });
        } else {
            // db.get 
            db.get(query, args, (err, row) => {
                if (err) {
                    reject(err); 
                } else {
                    resolve(row); 
                }
            });
        }
    });
}

function db_insert(query, args = []) {
    return new Promise((resolve, reject) => {
        db.run(query, args, function(err) {
            if (err) {
                reject(err); // On casse la promesse
            } else {
                resolve(this.lastID); // On valide avec le nouvel ID
            }
        });
    });
}

function db_update(query, args = []) {
    return new Promise((resolve, reject) => {
        db.run(query, args, function(err) {
            if (err) {
                reject(err); 
            } else {
                resolve(this.changes); 
            }
        });
    });
}

db.serialize(() => {


    db.run(`
        CREATE TABLE IF NOT EXISTS utilisateur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            est_parrain INTEGER NOT NULL
        )
    `);

    // 2. Table: demande_aide
    db.run(`
        CREATE TABLE IF NOT EXISTS demande_aide (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auteur_id INTEGER NOT NULL,
            matiere TEXT NOT NULL,
            description TEXT NOT NULL,
            statut TEXT DEFAULT 'ouverte',
            FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
        )
    `);

    // 3. Table: reponse
    db.run(`
        CREATE TABLE IF NOT EXISTS reponse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demande_id INTEGER NOT NULL,
            auteur_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (demande_id) REFERENCES demande_aide(id),
            FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
        )
    `);

    // 4. Table: parrainage
    db.run(`
        CREATE TABLE IF NOT EXISTS parrainage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parrain_id INTEGER NOT NULL,
            filleul_id INTEGER NOT NULL,
            FOREIGN KEY (parrain_id) REFERENCES utilisateur(id),
            FOREIGN KEY (filleul_id) REFERENCES utilisateur(id)
        )
    `);

    // 5. Table: ressource
    db.run(`
        CREATE TABLE IF NOT EXISTS ressource (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auteur_id INTEGER NOT NULL,
            matiere TEXT NOT NULL,
            titre TEXT NOT NULL,
            lien_url TEXT NOT NULL,
            FOREIGN KEY (auteur_id) REFERENCES utilisateur(id)
        )
    `);

    console.log("✅ Toutes les tables ont été créées avec succès !");
});

// Fermeture de la base de données une fois les requêtes terminées
// db.close((err) => {
//     if (err) {
//         console.error("Erreur", err.message);
//     } else {
//         console.log("Base de données fermée");
//     }
// });
//on exporte les fonctions utilitaires 
module.exports = {
    db,
    db_fetch,
    db_insert,
    db_update
};