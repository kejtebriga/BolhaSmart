from model import Oglas, Kategorija, Uporabnik

def izpisi_tabelo_oglasov(iterator_oglasov):
    """Pomožna funkcija za lepši izpis seznama."""
    print(f"\n{'ID':<4} | {'Tip':<8} | {'Naslov':<20} | {'Cena':<8}")
    print("-" * 50)
    st = 0
    for o in iterator_oglasov:
        print(f"{o.id:<4} | {o.tip:<8} | {o.naslov[:20]:<20} | {o.cena:>6} €")
        st += 1
    if st == 0:
        print("Ni zadetkov.")
    return st

def oddaj_oglas_z_matchmakingom():
    print("\n--- ODDAJA NOVEGA OGLASA ---")
    
    print("\n--- REGISTRIRAJ SE:")
    ime = input("Ime:")
    priimek = input("Priimek:")
    email = input("Email:")

    nov_uporabnik = Uporabnik.poisci_po_email(email)
    if not nov_uporabnik:
        nov_uporabnik = Uporabnik(None, ime, priimek, email)
        nov_uporabnik.vstavi_uporabnika()



    print("\nIzberi kategorijo izdelka:")
    kategorije = list(Kategorija.poisci_vse())
    for kat in kategorije:
        print(f"{kat.id}) {kat.naziv}")

    while True:
        try:
            kat_id = int(input("Vnesi ID kategorije: "))
        except ValueError:
            print("Napaka: ID mora biti številka!")
            continue  

        if any(kat.id == kat_id for kat in kategorije):
            break  
        else:
            print("Neveljaven ID kategorije! Poskusi znova.")


    
    naslov = input("Kaj prodajaš/kupuješ? ")
    opis = input("Vnesi kratek opis: ")
    
    try:
        cena = float(input("Cena: "))
    except ValueError:
        print("Napaka: Cena mora biti številka!")
        return

    tip = ""
    while tip not in ['prodaja', 'nakup']:
        tip = input("Vnesi tip (prodaja/nakup): ").lower()
    
    


    
    u_id = nov_uporabnik.id
    
    
    nov_oglas = Oglas(None, naslov, opis, cena, tip, u_id, kat_id)
    nov_oglas.vstavi()
    print(f"\n Oglas '{naslov}' je bil uspešno objavljen!")

    
    print("\n" " NAJDENA UJEMANJA ZA VAS " )
    ujemanja = list(Oglas.poisci_ujemanja(nov_oglas))
    
    if ujemanja:
        print(f"Našli smo {len(ujemanja)} oglasov, ki bi vas utegnili zanimati:")
        izpisi_tabelo_oglasov(ujemanja)
    else:
        print("Trenutno ni nasprotnih ponudb.")

def glavni_meni():
    while True:
        print("\n" + "="*40)
        print("       MOJ OGLASNIK - GLAVNI MENI")
        print("="*40)
        print("1) Brskaj po vseh oglasih")
        print("2) Išči oglase po ključni besedi")
        print("3) ODDAJ OGLAS (in najdi ujemanja)")
        print("4) Poglej podrobnosti oglasa (preko ID)")
        print("5) Prikaži kontaktne podatke (preko ID oglasa)")
        print("0) Izhod")
        
        izbira = input("\nIzberi možnost: ")
        
        if izbira == "1":
            izpisi_tabelo_oglasov(Oglas.poisci_vse())
        elif izbira == "2":
            niz = input("\nVpiši iskalni niz: ")
            izpisi_tabelo_oglasov(Oglas.isci_po_besedilu(niz))
        elif izbira == "3":
            oddaj_oglas_z_matchmakingom()
        elif izbira == "4":
            id_vnos = input("\nVnesi ID oglasa: ")
            o = Oglas.poisci_po_id(id_vnos)
            if o:
                print(f"\n--- PODROBNOSTI (ID: {o.id}) ---")
                print(f"Naslov: {o.naslov}\nTip: {o.tip}\nCena: {o.cena} €\nOpis: {o.opis}")
            else:
                print("Oglas ne obstaja.")
        elif izbira == "5":
            id_vnos = input("\nVnesi ID oglasa: ")
            o = Oglas.poisci_po_id(id_vnos)
            if o:
                u = Uporabnik.poisci_po_id(o.uporabnik_id)
                print(f"\n--- KONTAKTNI PODATKI ZA OGLAS {o.naslov}---")
                print(f"{u}")
            else:
                print("Oglas ne obstaja.")

        elif izbira == "0":
            print("Konec seje.")
            break
        else:
            print("Neveljavna izbira.")

if __name__ == "__main__":
    glavni_meni()
