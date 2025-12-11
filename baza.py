import sqlite3
import csv

PARAM_FMT = ":{}"   # za SQLite


class Tabela:
    """
    Osnovni razred za vse tabele v bazi.
    Vsebuje generične metode za dodajanje, brisanje, ustvarjanje in uvoz.
    """

    ime = None
    podatki = None

    def __init__(self, conn):
        """Shrani povezavo na bazo."""
        self.conn = conn

    def ustvari(self):
        """Metoda, ki jo mora podrazred prepisati in ustvariti tabelo."""
        raise NotImplementedError

    def izbrisi(self):
        """Izbriše tabelo, če obstaja."""
        self.conn.execute(f"DROP TABLE IF EXISTS {self.ime};")

    def uvozi(self, encoding="UTF-8"):
        """Uvozi podatke iz CSV, če je tabela povezana z datoteko."""
        if self.podatki is None:
            return
        with open(self.podatki, encoding=encoding) as f:
            podatki = csv.reader(f)
            stolpci = next(podatki)
            for vrstica in podatki:
                vrstica = {k: None if v == "" else v for k, v in zip(stolpci, vrstica)}
                self.dodaj_vrstico(**vrstica)

    def izprazni(self):
        """Izbriše vse vrstice v tabeli."""
        self.conn.execute(f"DELETE FROM {self.ime};")

    def dodajanje(self, stolpci=None):
        """Pripravi SQL INSERT ukaz glede na podane stolpce."""
        return f"""
            INSERT INTO {self.ime} ({", ".join(stolpci)})
            VALUES ({", ".join(PARAM_FMT.format(s) for s in stolpci)});
        """

    def dodaj_vrstico(self, **podatki):
        """Doda eno vrstico v tabelo in vrne ID vrstice."""
        podatki = {k: v for k, v in podatki.items() if v is not None}
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.conn.execute(poizvedba, podatki)
        return cur.lastrowid


# ===================================
# TABELE TVOJE APLIKACIJE
# ===================================

class Uporabnik(Tabela):
    """Tabela za uporabnike."""

    ime = "uporabnik"

    def ustvari(self):
        """Ustvari tabelo 'uporabnik'."""
        self.conn.execute("""
            CREATE TABLE uporabnik (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            );
        """)


class Izdelek(Tabela):
    """Tabela za izdelke."""

    ime = "izdelek"

    def ustvari(self):
        """Ustvari tabelo 'izdelek'."""
        self.conn.execute("""
            CREATE TABLE izdelek (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT NOT NULL,
                cena REAL NOT NULL
            );
        """)


class Oglas(Tabela):
    """Tabela za oglase."""

    ime = "oglas"

    def ustvari(self):
        """Ustvari tabelo 'oglas'."""
        self.conn.execute("""
            CREATE TABLE oglas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uporabnik_id INTEGER REFERENCES uporabnik(id),
                izdelek_id  INTEGER REFERENCES izdelek(id),
                opis TEXT
            );
        """)



# ===================================
# FUNKCIJE ZA DELO Z BAZO
# ===================================

def pripravi_tabele(conn):
    """Pripravi in vrne seznam objektov tabel."""
    uporabnik = Uporabnik(conn)
    izdelek = Izdelek(conn)
    oglas = Oglas(conn)
    return [uporabnik, izdelek, oglas]



def izbrisi_tabele(tabele):
    """Izbriše vse podane tabele iz baze."""
    for t in tabele:
        t.izbrisi()


def ustvari_tabele(tabele):
    """Ustvari vse podane tabele v bazi."""
    for t in tabele:
        t.ustvari()


def izprazni_tabele(tabele):
    """Izprazni vse podane tabele."""
    for t in tabele:
        t.izprazni()


def uvozi_podatke(tabele):
    """Uvozi podatke iz CSV v vse tabele, ki to podpirajo."""
    for t in tabele:
        t.uvozi()


def ustvari_bazo(conn):
    """Pobriše, ponovno ustvari in napolni celotno bazo."""
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)


def ustvari_bazo_ce_ne_obstaja(conn):
    """Ustvari bazo samo, če je trenutno prazna."""
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0,):
            ustvari_bazo(conn)


# ===================================
# TESTNI ZAGON (po želji)
# ===================================

if __name__ == "__main__":
     conn = sqlite3.connect("moja_baza.db")
     ustvari_bazo(conn)
     print("Baza ustvarjena.")
