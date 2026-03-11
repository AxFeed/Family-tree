CREATE DATABASE IF NOT EXISTS BobFamily;

USE BobFamily;

CREATE USER IF NOT EXISTS 'bob'@'%' IDENTIFIED BY 'ross';
GRANT SELECT, INSERT, UPDATE, DELETE ON BobFamily.* TO 'bob'@'%';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS Personne (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_naissance DATE NULL,
    date_mort DATE NULL,

    CONSTRAINT chk_dates_coherentes CHECK (date_mort >= date_naissance)
);

CREATE TABLE IF NOT EXISTS Prenom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_personne INT NOT NULL,
    prenom VARCHAR(255) NOT NULL,

    FOREIGN KEY (id_personne) REFERENCES Personne(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Nom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_personne INT NOT NULL,
    nom VARCHAR(100) NOT NULL,

    FOREIGN KEY (id_personne) REFERENCES Personne(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS LienParente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_enfant INT NOT NULL,
    id_parent INT NOT NULL,
    type_lien ENUM('BIOLOGIQUE', 'ADOPTIF', 'BEAU_PARENT') NOT NULL DEFAULT 'BIOLOGIQUE',

    FOREIGN KEY (id_enfant) REFERENCES Personne(id) ON DELETE CASCADE,
    FOREIGN KEY (id_parent) REFERENCES Personne(id) ON DELETE CASCADE,

    CONSTRAINT chk_pas_autoparent CHECK (id_enfant <> id_parent)
);

CREATE TABLE IF NOT EXISTS Couple (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_personne_1 INT NOT NULL,
    id_personne_2 INT NOT NULL,

    FOREIGN KEY (id_personne_1) REFERENCES Personne(id) ON DELETE CASCADE,
    FOREIGN KEY (id_personne_2) REFERENCES Personne(id) ON DELETE CASCADE,

    CONSTRAINT chk_pas_autocouple CHECK (id_personne_1 <> id_personne_2),
    CONSTRAINT chk_ordre_couple CHECK (id_personne_1 < id_personne_2)
);