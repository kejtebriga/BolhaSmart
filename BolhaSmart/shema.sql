DROP TABLE IF EXISTS oglas;
DROP TABLE IF EXISTS kategorija;
DROP TABLE IF EXISTS uporabnik;

CREATE TABLE uporabnik (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ime TEXT,
    priimek TEXT,
    email TEXT
);

CREATE TABLE kategorija (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv TEXT
);

CREATE TABLE oglas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naslov TEXT,
    opis TEXT,
    cena REAL,
    tip TEXT, 
    uporabnik_id INTEGER,
    kategorija_id INTEGER,
    FOREIGN KEY (uporabnik_id) REFERENCES uporabnik (id),
    FOREIGN KEY (kategorija_id) REFERENCES kategorija (id)
);

