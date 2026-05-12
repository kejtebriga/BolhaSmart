import bottle
import json
from functools import wraps
from model import Uporabnik, Oglas, Kategorija


SKRIVNOST = 'moja_skrivnost_za_piskotke_2024'


# ── Piškotki in sporočila ────────────────────────────────────────────────────

def izbrisi_piskotek(piskotek):
    bottle.response.delete_cookie(piskotek, path='/')


def nastavi_sporocilo(sporocilo, piskotek='sporocilo'):
    bottle.response.set_cookie(piskotek, sporocilo, secret=SKRIVNOST, path='/')


def preberi_sporocilo(piskotek='sporocilo', izbrisi=True):
    sporocilo = bottle.request.get_cookie(piskotek, secret=SKRIVNOST)
    if izbrisi:
        izbrisi_piskotek(piskotek)
    return sporocilo


def nastavi_obrazec(piskotek, obrazec):
    nastavi_sporocilo(json.dumps(obrazec), piskotek)


def preberi_obrazec(piskotek, privzeto=None, izbrisi=True):
    if privzeto is None:
        privzeto = {}
    try:
        privzeto.update(json.loads(preberi_sporocilo(piskotek, izbrisi)))
    except (TypeError, json.JSONDecodeError):
        pass
    return privzeto


# ── Prijava / odjava ─────────────────────────────────────────────────────────

def prijavljeni_uporabnik():
    idu = bottle.request.get_cookie('uporabnik', secret=SKRIVNOST)
    return Uporabnik.z_id(idu)


def prijavi_uporabnika(uporabnik, piskotek=None):
    if not uporabnik:
        nastavi_sporocilo("Prijava ni bila uspešna!")
        bottle.redirect('/prijava/')
    bottle.response.set_cookie('uporabnik', str(uporabnik.id), secret=SKRIVNOST, path='/')
    if piskotek:
        izbrisi_piskotek(piskotek)
    bottle.redirect('/')


def odjavi_uporabnika():
    izbrisi_piskotek('uporabnik')
    bottle.redirect('/')


# ── Dekoratorji ───────────────────────────────────────────────────────────────

def status(preveri):
    @wraps(preveri)
    def decorator(fun):
        @wraps(fun)
        def wrapper(*largs, **kwargs):
            uporabnik = prijavljeni_uporabnik()
            out = fun(*preveri(uporabnik), *largs, **kwargs)
            if out is None:
                out = {}
            if isinstance(out, dict):
                out['uporabnik'] = uporabnik
            return out
        return wrapper
    return decorator


@status
def admin(uporabnik):
    if not uporabnik or not uporabnik.admin:
        bottle.abort(401, "Dostop prepovedan! Samo za administratorje.")
    return (uporabnik,)


@status
def prijavljen(uporabnik):
    if not uporabnik:
        bottle.redirect('/prijava/')
    return (uporabnik,)


@status
def kdorkoli(uporabnik):
    return (uporabnik,)


@status
def odjavljen(uporabnik):
    if uporabnik:
        bottle.redirect('/')
    return ()


# ── Statične datoteke ─────────────────────────────────────────────────────────

@bottle.get('/static/<datoteka:path>')
def static(datoteka):
    return bottle.static_file(datoteka, root='static')


# ── Glavna stran ──────────────────────────────────────────────────────────────

@bottle.get('/')
@bottle.view('index.html')
@kdorkoli
def index(uporabnik):
    iskanje = bottle.request.query.iskanje
    kategorija_id = bottle.request.query.kategorija_id
    tip = bottle.request.query.tip

    oglasi = Oglas.poisci_vse()

    if iskanje:
        oglasi = [o for o in oglasi if iskanje.lower() in o.naslov.lower() or iskanje.lower() in (o.opis or '').lower()]
    if kategorija_id:
        oglasi = [o for o in oglasi if str(o.kategorija_id) == str(kategorija_id)]
    if tip:
        oglasi = [o for o in oglasi if o.tip == tip]

    kategorije = Kategorija.poisci_vse()
    return dict(oglasi=oglasi, iskanje=iskanje, kategorija_id=kategorija_id, tip=tip, kategorije=kategorije)


# ── Prijava ───────────────────────────────────────────────────────────────────

@bottle.get('/prijava/')
@bottle.view('prijava.html')
@odjavljen
def prijava():
    pass


@bottle.post('/prijava/')
@odjavljen
def prijava_post():
    email = bottle.request.forms.email
    geslo = bottle.request.forms.geslo
    nastavi_obrazec('prijava', {'email': email})
    u = Uporabnik.prijavi(email, geslo)
    if u is None:
        nastavi_sporocilo("Napačen email ali geslo!")
        bottle.redirect('/prijava/')
    prijavi_uporabnika(u, piskotek='prijava')


# ── Registracija ──────────────────────────────────────────────────────────────

@bottle.get('/registracija/')
@bottle.view('registracija.html')
@odjavljen
def registracija():
    pass


@bottle.post('/registracija/')
@odjavljen
def registracija_post():
    ime = bottle.request.forms.ime
    priimek = bottle.request.forms.priimek
    email = bottle.request.forms.email
    geslo = bottle.request.forms.geslo
    geslo2 = bottle.request.forms.geslo2

    nastavi_obrazec('registracija', {'ime': ime, 'priimek': priimek, 'email': email})

    if geslo != geslo2:
        nastavi_sporocilo("Gesli se ne ujemata!")
        bottle.redirect('/registracija/')

    u = Uporabnik(id=None, ime=ime, priimek=priimek, email=email)
    try:
        u.registriraj(geslo)
        prijavi_uporabnika(u, piskotek='registracija')
    except ValueError as e:
        nastavi_sporocilo(str(e))
        bottle.redirect('/registracija/')


# ── Odjava ────────────────────────────────────────────────────────────────────

@bottle.post('/odjava/')
@prijavljen
def odjava(uporabnik):
    odjavi_uporabnika()


# ── Moji oglasi ───────────────────────────────────────────────────────────────

@bottle.get('/moji-oglasi/')
@bottle.view('moji_oglasi.html')
@prijavljen
def moji_oglasi(uporabnik):
    vsi = Oglas.poisci_vse()
    oglasi = [o for o in vsi if o.uporabnik_id == uporabnik.id]
    # slovar kategorij za hitro iskanje po id-ju
    kategorije = {k.id: k for k in Kategorija.poisci_vse()}
    return dict(oglasi=oglasi, kategorije=kategorije)


# ── Oglas podatki ─────────────────────────────────────────────────────────────

@bottle.get('/oglasi/podatki/<ido:int>/')
@bottle.view('oglas_podatki.html')
@kdorkoli
def oglas_podatki(uporabnik, ido):
    oglas = Oglas.poisci_po_id(ido)
    if oglas is None:
        bottle.abort(404, "Oglas ne obstaja.")
    lastnik = Uporabnik.poisci_po_id(oglas.uporabnik_id)
    kategorija = None
    for k in Kategorija.poisci_vse():
        if k.id == oglas.kategorija_id:
            kategorija = k
            break
    ujemanja = Oglas.poisci_ujemanja(oglas)
    return dict(oglas=oglas, lastnik=lastnik, kategorija=kategorija, ujemanja=ujemanja)


# ── Dodaj oglas ───────────────────────────────────────────────────────────────

@bottle.get('/oglasi/dodaj/')
@bottle.view('oglas_obrazec.html')
@prijavljen
def oglasi_dodaj(uporabnik):
    kategorije = Kategorija.poisci_vse()
    obrazec = preberi_obrazec('oglas_obrazec')
    return dict(naslov_strani='Oddaj oglas', akcija='/oglasi/dodaj/', kategorije=kategorije, obrazec=obrazec)


@bottle.post('/oglasi/dodaj/')
@prijavljen
def oglasi_dodaj_post(uporabnik):
    naslov = bottle.request.forms.naslov
    opis = bottle.request.forms.opis
    cena_raw = bottle.request.forms.cena.strip()
    tip = bottle.request.forms.tip
    kategorija_id = bottle.request.forms.kategorija_id

    try:
        cena = float(cena_raw) if cena_raw else None
    except ValueError:
        cena = None

    oglas = Oglas(id=None, naslov=naslov, opis=opis, cena=cena,
                  tip=tip, uporabnik_id=uporabnik.id, kategorija_id=kategorija_id)
    oglas.vstavi()
    nastavi_sporocilo("✓ Oglas je bil uspešno dodan!")
    bottle.redirect('/moji-oglasi/')


# ── Uredi oglas ───────────────────────────────────────────────────────────────

@bottle.get('/oglasi/uredi/<ido:int>/')
@bottle.view('oglas_obrazec.html')
@prijavljen
def oglasi_uredi(uporabnik, ido):
    oglas = Oglas.poisci_po_id(ido)
    if oglas is None:
        bottle.abort(404, "Oglas ne obstaja.")
    if oglas.uporabnik_id != uporabnik.id and not uporabnik.admin:
        bottle.abort(401, "Nimate pravice urejati tega oglasa.")
    kategorije = Kategorija.poisci_vse()
    obrazec = preberi_obrazec('oglas_obrazec', {
        'naslov': oglas.naslov, 'opis': oglas.opis, 'cena': oglas.cena,
        'tip': oglas.tip, 'kategorija_id': oglas.kategorija_id
    })
    return dict(naslov_strani='Uredi oglas', akcija=f'/oglasi/uredi/{ido}/', kategorije=kategorije, obrazec=obrazec)


@bottle.post('/oglasi/uredi/<ido:int>/')
@prijavljen
def oglasi_uredi_post(uporabnik, ido):
    oglas = Oglas.poisci_po_id(ido)
    if oglas is None:
        bottle.abort(404, "Oglas ne obstaja.")
    if oglas.uporabnik_id != uporabnik.id and not uporabnik.admin:
        bottle.abort(401, "Nimate pravice urejati tega oglasa.")

    naslov = bottle.request.forms.naslov
    opis = bottle.request.forms.opis
    cena = bottle.request.forms.cena or None
    tip = bottle.request.forms.tip
    kategorija_id = bottle.request.forms.kategorija_id

    oglas.naslov = naslov
    oglas.opis = opis
    oglas.cena = float(cena) if cena else None
    oglas.tip = tip
    oglas.kategorija_id = kategorija_id

    try:
        oglas.posodobi()
        nastavi_sporocilo("✓ Oglas je bil uspešno posodobljen!")
        bottle.redirect(f'/oglasi/podatki/{ido}/')
    except Exception:
        nastavi_sporocilo("Napaka pri urejanju oglasa!")
        bottle.redirect(f'/oglasi/uredi/{ido}/')


# ── Izbriši oglas ─────────────────────────────────────────────────────────────

@bottle.post('/oglasi/izbrisi/<ido:int>/')
@prijavljen
def oglasi_izbrisi(uporabnik, ido):
    oglas = Oglas.poisci_po_id(ido)
    if oglas is None:
        bottle.abort(404, "Oglas ne obstaja.")
    if oglas.uporabnik_id != uporabnik.id and not uporabnik.admin:
        bottle.abort(401, "Nimate pravice brisati tega oglasa.")
    try:
        oglas.izbrisi()
        nastavi_sporocilo("✓ Oglas je bil izbrisan.")
    except Exception:
        nastavi_sporocilo("Napaka pri brisanju oglasa!")
    bottle.redirect('/')


# ── Admin: uporabniki ─────────────────────────────────────────────────────────

@bottle.get('/admin/uporabniki/')
@bottle.view('admin_uporabniki.html')
@admin
def admin_uporabniki(uporabnik):
    vsi = Uporabnik.poisci_vse()
    return dict(vsi_uporabniki=vsi)


@bottle.get('/admin/uporabniki/<idu:int>/')
@bottle.view('admin_uporabnik_uredi.html')
@admin
def admin_uporabnik_uredi(uporabnik, idu):
    target = Uporabnik.poisci_po_id(idu)
    return dict(target=target)


@bottle.post('/admin/uporabniki/<idu:int>/')
@admin
def admin_uporabnik_uredi_post(uporabnik, idu):
    ime = bottle.request.forms.ime
    priimek = bottle.request.forms.priimek
    email = bottle.request.forms.email
    target = Uporabnik(id=idu, ime=ime, priimek=priimek, email=email)
    try:
        target.posodobi()
        nastavi_sporocilo("✓ Podatki so bili uspešno posodobljeni.")
    except Exception:
        nastavi_sporocilo("Napaka pri posodabljanju!")
    bottle.redirect('/admin/uporabniki/')


# ── Globalne predloge ─────────────────────────────────────────────────────────

bottle.BaseTemplate.defaults['prijavljeni_uporabnik'] = prijavljeni_uporabnik
bottle.BaseTemplate.defaults['preberi_sporocilo'] = preberi_sporocilo
bottle.BaseTemplate.defaults['preberi_obrazec'] = preberi_obrazec


if __name__ == '__main__':
    bottle.run(debug=True, reloader=True)