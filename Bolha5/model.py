import sqlite3 as dbapi
import bcrypt

BAZA = "moja_baza.db"


class Uporabnik:
    def __init__(self, id, ime, priimek, email, geslo=None, admin=False):
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.email = email
        self.geslo = geslo
        self.admin = bool(admin)

    def __str__(self):
        return f"{self.ime} {self.priimek} ({self.email})"

    def __bool__(self):
        return self.id is not None

    @staticmethod
    def _iz_vrstice(v):
        return Uporabnik(v['id'], v['ime'], v['priimek'], v['email'], v['geslo'], v['admin'])

    @staticmethod
    def poisci_vse():
        """Vrne seznam vseh uporabnikov."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id, ime, priimek, email, geslo, admin FROM uporabnik")
            return [Uporabnik._iz_vrstice(v) for v in cur]

    @staticmethod
    def poisci_po_id(uporabnik_id):
        """Poišče enega uporabnika glede na ID."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM uporabnik WHERE id = ?", (uporabnik_id,))
            v = cur.fetchone()
            return Uporabnik._iz_vrstice(v) if v else None

    @staticmethod
    def z_id(idu):
        """Vrni uporabnika z ID-jem iz piškotka."""
        if not idu:
            return None
        try:
            idu = int(idu)
        except (ValueError, TypeError):
            return None
        return Uporabnik.poisci_po_id(idu)

    @staticmethod
    def poisci_po_email(email):
        """Poišče uporabnika po email naslovu."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM uporabnik WHERE email = ?", (email,))
            v = cur.fetchone()
            return Uporabnik._iz_vrstice(v) if v else None

    @staticmethod
    def _zgostitev(geslo):
        """Vrni bcrypt zgostitev gesla."""
        sol = bcrypt.gensalt()
        return bcrypt.hashpw(geslo.encode('utf-8'), sol)

    @staticmethod
    def prijavi(email, geslo):
        """Preveri email in geslo ter vrni uporabnika."""
        u = Uporabnik.poisci_po_email(email)
        if u is None or not u.geslo:
            return None
        geslo_bytes = u.geslo if isinstance(u.geslo, bytes) else u.geslo.encode('utf-8')
        if bcrypt.checkpw(geslo.encode('utf-8'), geslo_bytes):
            return u
        return None

    def registriraj(self, geslo):
        """Vstavi novega uporabnika v bazo z bcrypt geslom."""
        conn = dbapi.connect(BAZA)
        zgostitev = self._zgostitev(geslo)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO uporabnik (ime, priimek, email, geslo, admin)
                    VALUES (?, ?, ?, ?, 0)
                """, (self.ime, self.priimek, self.email, zgostitev))
                self.id = cur.lastrowid
        except dbapi.IntegrityError:
            raise ValueError("Email naslov je že v uporabi!")

    def posodobi(self):
        """Posodobi ime, priimek in email uporabnika v bazi."""
        conn = dbapi.connect(BAZA)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE uporabnik SET ime=?, priimek=?, email=? WHERE id=?
            """, (self.ime, self.priimek, self.email, self.id))


class Kategorija:
    def __init__(self, id, naziv):
        self.id = id
        self.naziv = naziv

    def __str__(self):
        return self.naziv

    @staticmethod
    def poisci_vse():
        """Vrne vse kategorije iz baze, urejene po ID-ju."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id, naziv FROM kategorija ORDER BY id")
            return [Kategorija(v['id'], v['naziv']) for v in cur]


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
        """Vrne vse oglase iz baze, urejene od najnovejšega."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM oglas ORDER BY id DESC")
            return [Oglas(v['id'], v['naslov'], v['opis'], v['cena'],
                         v['tip'], v['uporabnik_id'], v['kategorija_id']) for v in cur]

    @staticmethod
    def poisci_po_id(id_oglasa):
        """Poišče en oglas po ID-ju."""
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
    def poisci_po_uporabniku(uporabnik_id):
        """Vrne vse oglase določenega uporabnika."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM oglas WHERE uporabnik_id = ? ORDER BY id DESC
            """, (uporabnik_id,))
            return [Oglas(v['id'], v['naslov'], v['opis'], v['cena'],
                         v['tip'], v['uporabnik_id'], v['kategorija_id']) for v in cur]

    @staticmethod
    def poisci_filtrirane(iskanje=None, kategorija_id=None, tip=None):
        """Vrne filtrirane oglase z SQL poizvedbo."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        pogoji = []
        parametri = []
        if iskanje:
            pogoji.append("(naslov LIKE ? OR opis LIKE ?)")
            parametri += [f"%{iskanje}%", f"%{iskanje}%"]
        if kategorija_id:
            pogoji.append("kategorija_id = ?")
            parametri.append(kategorija_id)
        if tip:
            pogoji.append("tip = ?")
            parametri.append(tip)
        sql = "SELECT * FROM oglas"
        if pogoji:
            sql += " WHERE " + " AND ".join(pogoji)
        sql += " ORDER BY id DESC"
        with conn:
            cur = conn.cursor()
            cur.execute(sql, parametri)
            return [Oglas(v['id'], v['naslov'], v['opis'], v['cena'],
                         v['tip'], v['uporabnik_id'], v['kategorija_id']) for v in cur]

    @staticmethod
    def isci_po_besedilu(niz):
        """Vrne oglase, kjer se niz pojavi v naslovu ali opisu."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        with conn:
            cur = conn.cursor()
            iskanje = f"%{niz}%"
            cur.execute("""
                SELECT * FROM oglas WHERE naslov LIKE ? OR opis LIKE ?
                ORDER BY id DESC
            """, (iskanje, iskanje))
            for v in cur:
                yield Oglas(v['id'], v['naslov'], v['opis'], v['cena'],
                            v['tip'], v['uporabnik_id'], v['kategorija_id'])

    def vstavi(self):
        """Vstavi trenutni oglas v bazo."""
        conn = dbapi.connect(BAZA)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO oglas (naslov, opis, cena, tip, uporabnik_id, kategorija_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.naslov, self.opis, self.cena, self.tip, self.uporabnik_id, self.kategorija_id))
            self.id = cur.lastrowid

    def posodobi(self):
        """Posodobi oglas v bazi."""
        conn = dbapi.connect(BAZA)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE oglas SET naslov=?, opis=?, cena=?, tip=?, kategorija_id=?
                WHERE id=?
            """, (self.naslov, self.opis, self.cena, self.tip, self.kategorija_id, self.id))

    @staticmethod
    def poisci_ujemanja(moj_oglas):
        """Poišče ujemajoče oglase (ista kategorija, nasproten tip) z JOIN na kategorijo."""
        conn = dbapi.connect(BAZA)
        conn.row_factory = dbapi.Row
        nasproten_tip = 'nakup' if moj_oglas.tip == 'prodaja' else 'prodaja'
        with conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT oglas.id, oglas.naslov, oglas.opis, oglas.cena,
                       oglas.tip, oglas.uporabnik_id, oglas.kategorija_id
                FROM oglas
                JOIN kategorija ON oglas.kategorija_id = kategorija.id
                WHERE oglas.kategorija_id = ? AND oglas.tip = ? AND oglas.id != ?
                ORDER BY oglas.id DESC
            """, (moj_oglas.kategorija_id, nasproten_tip, moj_oglas.id))
            return [Oglas(v['id'], v['naslov'], v['opis'], v['cena'],
                         v['tip'], v['uporabnik_id'], v['kategorija_id'])
                    for v in cur]

    def izbrisi(self):
        """Izbriši oglas iz baze."""
        conn = dbapi.connect(BAZA)
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM oglas WHERE id=?", (self.id,))
            self.id = None