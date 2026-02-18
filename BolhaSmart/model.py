import sqlite3 as dbapi


BAZA = "moja_baza.db"

class Uporabnik:
    def __init__(self, id, ime, priimek, email):
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.email = email

    def __str__(self):
        return f"{self.ime} {self.priimek} ({self.email})"

    @staticmethod
    def poisci_vse():
        """Metoda, ki iz baze prebere use uporabnike in vrne tabelo objektov uporabnik."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id, ime, priimek, email FROM uporabnik")
            uporabniki = []
            for v in cur:
                uporabniki.append(Uporabnik(v['id'], v['ime'], v['priimek'], v['email']))
            return uporabniki


    @staticmethod
    def poisci_po_id(uporabnik_id):
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM uporabnik WHERE id = ?", (uporabnik_id,))
            v = cur.fetchone()
            if v:
                return Uporabnik(v['id'], v['ime'], v['priimek'], v['email'])
            return None
        
    def vstavi_uporabnika(self):
        conn = dbapi.connect(BAZA)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO uporabnik (ime, priimek, email)
                VALUES (?, ?, ?)
            """, (self.ime, self.priimek, self.email))
            self.id = cur.lastrowid
    
    @staticmethod
    def poisci_po_email(email):
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM uporabnik WHERE email = ?", (email,))
            v = cur.fetchone()
            if v:
                return Uporabnik(v['id'], v['ime'], v['priimek'], v['email'])
            return None


class Kategorija:
    def __init__(self, id, naziv):
        self.id = id
        self.naziv = naziv

    def __str__(self):
        return self.naziv

    @staticmethod
    def poisci_vse():
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id, naziv FROM kategorija ORDER BY naziv")
            kategorije = []
            for v in cur:
                kategorije.append(Kategorija(v['id'], v['naziv']))
            return kategorije



class Oglas:
    def __init__(self, id, naslov, opis, cena, tip, uporabnik_id, kategorija_id):
        self.id = id
        self.naslov = naslov
        self.opis = opis
        self.cena = cena
        self.tip = tip
        self.uporabnik_id = uporabnik_id
        self.kategorija_id = kategorija_id

    def __str__(self):
        return f"{self.naslov} ({self.cena} €)"

    @staticmethod
    def poisci_vse():
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM oglas")
            oglasi = []
            for v in cur:
                oglasi.append(Oglas(v['id'], v['naslov'], v['opis'], v['cena'], 
                            v['tip'], v['uporabnik_id'], v['kategorija_id']))
            return oglasi

    @staticmethod
    def poisci_po_id(id_oglasa):
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM oglas WHERE id = ?", (id_oglasa,))
            v = cur.fetchone()
            if v:
                return Oglas(v['id'], v['naslov'], v['opis'], v['cena'], 
                            v['tip'], v['uporabnik_id'], v['kategorija_id'])
            return None


    @staticmethod
    def isci_po_besedilu(niz):
        """Iskalnik po naslovu ali opisu (uporabno za trgovino)."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            iskanje = f"%{niz}%"
            cur.execute("SELECT * FROM oglas WHERE naslov LIKE ? OR opis LIKE ?", (iskanje, iskanje))
            for v in cur:
                yield Oglas(v['id'], v['naslov'], v['opis'], v['cena'], 
                            v['tip'], v['uporabnik_id'], v['kategorija_id'])

    def vstavi(self):
        conn = dbapi.connect(BAZA)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO oglas (naslov, opis, cena, tip, uporabnik_id, kategorija_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.naslov, self.opis, self.cena, self.tip, self.uporabnik_id, self.kategorija_id))
            self.id = cur.lastrowid
            
    @staticmethod
    def poisci_ujemanja(moj_oglas):
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
    
        nasproten_tip = 'nakup' if moj_oglas.tip == 'prodaja' else 'prodaja'
        moje_besede = set(moj_oglas.naslov.lower().split())
    
        with conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM oglas
                WHERE kategorija_id = ?
                  AND tip = ?
                  AND id != ?
            """, (moj_oglas.kategorija_id, nasproten_tip, moj_oglas.id))
            ujemanja = []
            for v in cur:
                naslov = v['naslov'].lower()
                if moje_besede & set(naslov.split()):
                    ujemanja.append(Oglas(
                        v['id'], v['naslov'], v['opis'], v['cena'],
                        v['tip'], v['uporabnik_id'], v['kategorija_id']
                    ))
            return ujemanja

