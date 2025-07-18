-- ajout de main pour correspondre a django et a sa structure de projet

CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMPTZ NOT NULL
);


CREATE TABLE main_credituser (
    id SERIAL PRIMARY KEY,
    credit NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    user_id INTEGER NOT NULL UNIQUE,
    CONSTRAINT fk_main_credituser_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);


CREATE TABLE main_adresseuser (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) NOT NULL,
    type_voie VARCHAR(100) NOT NULL,
    nom_rue VARCHAR(100) NOT NULL,
    complement VARCHAR(100),
    code_postal INTEGER NOT NULL,
    ville VARCHAR(100) NOT NULL,
    pays VARCHAR(100) NOT NULL DEFAULT 'Pays',
    telephone VARCHAR(10),
    email VARCHAR(100),
    photo VARCHAR(100) DEFAULT 'photo_default/photo_default.jpg',
    user_id INTEGER NOT NULL UNIQUE,
    CONSTRAINT fk_main_adresseuser_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);


CREATE TABLE main_choixrole (
    id SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL DEFAULT 'passager',
    user_id INTEGER NOT NULL UNIQUE,
    CONSTRAINT fk_main_choixrole_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);


CREATE TABLE main_voiture (
    id SERIAL PRIMARY KEY,
    marque VARCHAR(30) NOT NULL DEFAULT 'Marque',
    modele VARCHAR(50) NOT NULL DEFAULT 'Modele',
    couleur VARCHAR(50) NOT NULL DEFAULT 'Couleur',
    type_moteur VARCHAR(50) NOT NULL,
    places VARCHAR(20) NOT NULL DEFAULT 'Nombre de places',
    immatriculation VARCHAR(10) NOT NULL,
    annee INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE),
    user_id INTEGER,
    CONSTRAINT fk_main_voiture_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

CREATE TABLE main_trajetproposer (
    id SERIAL PRIMARY KEY,
    etat VARCHAR(15) NOT NULL DEFAULT 'Disponible',
    trajet_rembourser BOOLEAN NOT NULL DEFAULT FALSE,
    ville_depart VARCHAR(50) NOT NULL,
    ville_arrivee VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    heure TIME NOT NULL,
    places INTEGER NOT NULL,
    prix NUMERIC(5, 2) NOT NULL,
    total_payer NUMERIC(5, 2) DEFAULT 0.00,
    temps_trajet INTERVAL NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    chauffeur_id INTEGER NOT NULL,
    voiture_id INTEGER,
    CONSTRAINT fk_main_trajetproposer_chauffeur FOREIGN KEY (chauffeur_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_main_trajetproposer_voiture FOREIGN KEY (voiture_id) REFERENCES main_voiture(id) ON DELETE CASCADE
);


CREATE TABLE main_noteuser (
    id SERIAL PRIMARY KEY,
    note NUMERIC(2, 1),
    note_attribuee BOOLEAN NOT NULL DEFAULT FALSE,
    avis VARCHAR(100) NOT NULL DEFAULT 'oui',
    avis_donne BOOLEAN NOT NULL DEFAULT FALSE,
    commentaire TEXT,
    commentaire_attribuee BOOLEAN NOT NULL DEFAULT FALSE,
    commentaire_moderer BOOLEAN NOT NULL DEFAULT FALSE,
    etat_paiement VARCHAR(20) NOT NULL DEFAULT 'Payer',
    decision_prise BOOLEAN NOT NULL DEFAULT FALSE,
    token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    passager_id INTEGER,
    chauffeur_id INTEGER,
    trajet_id INTEGER,
    CONSTRAINT fk_main_noteuser_passager FOREIGN KEY (passager_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    CONSTRAINT fk_main_noteuser_chauffeur FOREIGN KEY (chauffeur_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    CONSTRAINT fk_main_noteuser_trajet FOREIGN KEY (trajet_id) REFERENCES main_trajetproposer(id) ON DELETE SET NULL,
    CONSTRAINT unique_main_note_per_trajet_user UNIQUE (chauffeur_id, passager_id, trajet_id)
);


CREATE TABLE main_tokenvalidation (
    id SERIAL PRIMARY KEY,
    token VARCHAR(128) NOT NULL UNIQUE,
    action VARCHAR(20) NOT NULL DEFAULT 'default_action',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id INTEGER NOT NULL UNIQUE,
    CONSTRAINT fk_main_tokenvalidation_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);


CREATE TABLE main_activationtoken (
    id SERIAL PRIMARY KEY,
    token VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id INTEGER NOT NULL UNIQUE,
    CONSTRAINT fk_main_activationtoken_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);


CREATE TABLE main_preference (
    id SERIAL PRIMARY KEY,
    exigences_particulieres VARCHAR(50) NOT NULL DEFAULT 'Pas d''exigences particulières',
    exigences_personnelles TEXT,
    fumeur VARCHAR(50) NOT NULL DEFAULT 'Non_fumeur',
    animaux VARCHAR(50) NOT NULL DEFAULT 'Animaux',
    user_preference_id INTEGER UNIQUE,
    CONSTRAINT fk_main_preference_user FOREIGN KEY (user_preference_id) REFERENCES auth_user(id) ON DELETE SET NULL
);


CREATE TABLE main_reservationtrajet (
    id SERIAL PRIMARY KEY,
    prix_par_passager NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    places INTEGER,
    etat_reservation VARCHAR(20) NOT NULL DEFAULT 'Reserver',
    reservation_rembourser BOOLEAN NOT NULL DEFAULT FALSE,
    etat_paiement VARCHAR(20) NOT NULL DEFAULT 'Payer',
    trajet_payer BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trajet_reserver_id INTEGER,
    passager_id INTEGER,
    CONSTRAINT fk_main_reservationtrajet_trajet FOREIGN KEY (trajet_reserver_id) REFERENCES main_trajetproposer(id) ON DELETE SET NULL,
    CONSTRAINT fk_main_reservationtrajet_passager FOREIGN KEY (passager_id) REFERENCES auth_user(id) ON DELETE SET NULL
);


CREATE TABLE main_changestatuttrajet (
    id SERIAL PRIMARY KEY,
    statut VARCHAR(15) NOT NULL DEFAULT 'Disponible',
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trajet_id INTEGER,
    CONSTRAINT fk_main_changestatuttrajet_trajet FOREIGN KEY (trajet_id) REFERENCES main_trajetproposer(id) ON DELETE CASCADE
);



-- Index sur les clés étrangères pour accélérer les jointures
CREATE INDEX idx_main_credituser_user_id ON main_credituser (user_id);
CREATE INDEX idx_main_adresseuser_user_id ON main_adresseuser (user_id);
CREATE INDEX idx_main_choixrole_user_id ON main_choixrole (user_id);
CREATE INDEX idx_main_voiture_user_id ON main_voiture (user_id);
CREATE INDEX idx_main_trajetproposer_chauffeur_id ON main_trajetproposer (chauffeur_id);
CREATE INDEX idx_main_trajetproposer_voiture_id ON main_trajetproposer (voiture_id);
CREATE INDEX idx_main_noteuser_passager_id ON main_noteuser (passager_id);
CREATE INDEX idx_main_noteuser_chauffeur_id ON main_noteuser (chauffeur_id);
CREATE INDEX idx_main_noteuser_trajet_id ON main_noteuser (trajet_id);
CREATE INDEX idx_main_tokenvalidation_user_id ON main_tokenvalidation (user_id);
CREATE INDEX idx_main_activationtoken_user_id ON main_activationtoken (user_id);
CREATE INDEX idx_main_preference_user_preference_id ON main_preference (user_preference_id);
CREATE INDEX idx_main_reservationtrajet_passager_id ON main_reservationtrajet (passager_id);
CREATE INDEX idx_main_reservationtrajet_trajet_reserver_id ON main_reservationtrajet (trajet_reserver_id);
CREATE INDEX idx_main_changestatuttrajet_trajet_id ON main_changestatuttrajet (trajet_id);

-- Index pour les champs fréquemment utilisés dans les clauses WHERE
CREATE INDEX idx_main_trajetproposer_ville_depart ON main_trajetproposer (ville_depart);
CREATE INDEX idx_main_trajetproposer_ville_arrivee ON main_trajetproposer (ville_arrivee);
CREATE INDEX idx_main_trajetproposer_date ON main_trajetproposer (date);
CREATE INDEX idx_main_trajetproposer_etat ON main_trajetproposer (etat);
CREATE INDEX idx_main_reservationtrajet_etat_reservation ON main_reservationtrajet (etat_reservation);
