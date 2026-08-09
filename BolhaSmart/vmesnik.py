from model import Oglas, Kategorija, Uporabnik


def cena_str(cena):
    """Vrne ceno kot niz; če manjka (None ali prazno), vrne 'po dogovoru'."""
    try:
        return f"{float(cena):.2f} €"
    except (TypeError, ValueError):
        return "po dogovoru"


def izpisi_tabelo_oglasov(iterator_oglasov):
    """Pomožna funkcija za lepši izpis seznama."""
    print(f"\n{'ID':<4} | {'Tip':<8} | {'Naslov':<20} | {'Cena':<12}")
    print("-" * 54)
    st = 0
    for o in iterator_oglasov:
        print(f"{o.id:<4} | {o.tip:<8} | {o.naslov[:20]:<20} | {cena_str(o.cena)}")
        st += 1
    if st == 0:
        print("Ni zadetkov.")
    return st


# ── Pomožne funkcije za branje vnosov ────────────────────────────────────

def vnesi_ceno():
    """Prebere ceno. Prazen vnos pomeni 'po dogovoru' (None).
    Ob ne-številskem vnosu ponovi samo vnos cene."""
    while True:
        vnos = input("Cena (pusti prazno za po dogovoru): ").strip()
        if vnos == "":
            return None
        try:
            return float(vnos.replace(",", "."))
        except ValueError:
            print("Napaka: cena mora biti število (ali prazno za 'po dogovoru').")


def vnesi_tip():
    """Prebere tip oglasa (prodaja/nakup). Ob napačnem vnosu ponovi."""
    while True:
        tip = input("Tip (prodaja/nakup): ").strip().lower()
        if tip in ("prodaja", "nakup"):
            return tip
        print("Napaka: vnesi 'prodaja' ali 'nakup'.")


def vnesi_kategorijo(kategorije):
    """Izpiše kategorije in prebere veljaven ID. Ob napačnem vnosu ponovi."""
    print("\nIzberi kategorijo izdelka:")
    for kat in kategorije:
        print(f"{kat.id}) {kat.naziv}")
    veljavni = {kat.id for kat in kategorije}
    while True:
        vnos = input("Vnesi številko kategorije: ").strip()
        try:
            kat_id = int(vnos)
        except ValueError:
            print("Napaka: številka ni pravilna")
            continue
        if kat_id in veljavni:
            return kat_id
        print("Napaka: številka ni pravilna")


# ── Prijava / registracija (ločeno od oddaje oglasa) ─────────────────────

def prijava_ali_registracija():
    """Prijavi ali registrira uporabnika in ga vrne. Ob neuspehu vrne None."""
    print("\n--- PRIJAVA / REGISTRACIJA ---")
    email = input("Email: ").strip()
    uporabnik = Uporabnik.poisci_po_email(email)

    if uporabnik:
        # obstoječi uporabnik -> prijava z geslom
        geslo = input("Geslo: ")
        preverjen = Uporabnik.prijavi(email, geslo)
        if preverjen:
            print(f"Prijavljeni ste kot {preverjen.ime} {preverjen.priimek}.")
            return preverjen
        print("Napačno geslo.")
        return None

    # nov uporabnik -> registracija
    print("Uporabnik s tem emailom še ne obstaja – registracija.")
    ime = input("Ime: ").strip()
    priimek = input("Priimek: ").strip()
    geslo = input("Geslo: ")
    nov = Uporabnik(None, ime, priimek, email)
    try:
        nov.registriraj(geslo)
    except ValueError as e:
        print(f"Napaka: {e}")
        return None
    print("Registracija uspešna, prijavljeni ste.")
    return nov


# ── Oddaja oglasa (uporabnik je že prijavljen) ───────────────────────────

def oddaj_oglas(uporabnik):
    """Oddaja novega oglasa za že prijavljenega uporabnika + prikaz ujemanj."""
    print("\n--- ODDAJA NOVEGA OGLASA ---")

    kategorije = list(Kategorija.poisci_vse())
    kat_id = vnesi_kategorijo(kategorije)

    naslov = input("Kaj prodajaš/kupuješ? ")
    opis = input("Vnesi kratek opis: ")
    cena = vnesi_ceno()
    tip = vnesi_tip()

    nov_oglas = Oglas(None, naslov, opis, cena, tip, uporabnik.id, kat_id)
    nov_oglas.vstavi()
    print(f"\n Oglas '{naslov}' je bil uspešno objavljen!")

    print("\n NAJDENA UJEMANJA ZA VAS ")
    ujemanja = list(Oglas.poisci_ujemanja(nov_oglas))
    if ujemanja:
        print(f"Našli smo {len(ujemanja)} oglasov, ki bi vas utegnili zanimati:")
        izpisi_tabelo_oglasov(ujemanja)
    else:
        print("Trenutno ni nasprotnih ponudb.")


# ── Glavni meni ──────────────────────────────────────────────────────────

def glavni_meni():
    trenutni_uporabnik = None
    while True:
        print("\n" + "=" * 40)
        print("       BOLHA-SMART")
        print("=" * 40)
        if trenutni_uporabnik:
            print(f"Prijavljeni: {trenutni_uporabnik.ime} {trenutni_uporabnik.priimek}")
        else:
            print("Niste prijavljeni.")
        print("-" * 40)
        print("0 Izhod")
        print("1 Prikaži vse oglase")
        print("2 Išči s ključno besedo")
        print("3 Prijava / registracija")
        print("4 Ustvari oglas (in najdi ujemanja)")
        print("5 Poglej podrobnosti oglasa")   # (preko ID)
        print("6 Prikaži kontaktne podatke")    # (preko ID oglasa)

        izbira = input("\nIzberi možnost: ")

        if izbira == "1":
            izpisi_tabelo_oglasov(Oglas.poisci_vse())

        elif izbira == "2":
            niz = input("\nKaj iščeš: ")
            izpisi_tabelo_oglasov(Oglas.isci_po_besedilu(niz))

        elif izbira == "3":
            uporabnik = prijava_ali_registracija()
            if uporabnik:
                trenutni_uporabnik = uporabnik

        elif izbira == "4":
            if not trenutni_uporabnik:
                print("Za oddajo oglasa se najprej prijavite (možnost 3).")
            else:
                oddaj_oglas(trenutni_uporabnik)

        elif izbira == "5":
            id_vnos = input("\nVnesi ID oglasa: ")
            o = Oglas.poisci_po_id(id_vnos)
            if o:
                print(f"\n--- PODROBNOSTI (ID: {o.id}) ---")
                print(f"Naslov: {o.naslov}")
                print(f"Tip: {o.tip}")
                print(f"Cena: {cena_str(o.cena)}")
                print(f"Opis: {o.opis}")
            else:
                print("Oglas ne obstaja.")

        elif izbira == "6":
            id_vnos = input("\nVnesi ID oglasa: ")
            o = Oglas.poisci_po_id(id_vnos)
            if o:
                u = Uporabnik.poisci_po_id(o.uporabnik_id)
                print(f"\n--- KONTAKTNI PODATKI ZA OGLAS {o.naslov}---")
                print(f"{u}")
            else:
                print("Oglas ne obstaja.")

        elif izbira == "0":
            break
        # gremo ven iz vmesnika
        else:
            print("Neveljavno število.")


if __name__ == "__main__":
    glavni_meni()