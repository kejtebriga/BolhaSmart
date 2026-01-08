#BolhaSmart

##Namen:
Namen projekta je ustvariti aplikacijo za prodajo in nakup rabljenih predmetov. Uporabnik lahko odda oglas za nakup ali prodajo, aplikacija pa mu samodejno vrne oglase nasprotnega tipa, ki se ujemajo glede na kategorijo in ključne besede v naslovu.

##Funkcionalnosti:
Pregled vseh oglasov: Uporabniku se izpišejo vsi oglasi za nakup in prodajo.
Brskanje po kategorijah: Uporabnik izbere kategorijo, aplikacija pa prikaže ustrezne oglase.
Iskanje po ključnih besedah: Oglase je mogoče filtrirati glede na besedo, ki se pojavi v naslovu oglasa.
Filtriranje po ceni in tipu: Uporabnik lahko omeji izpis oglasov glede na maksimalno ceno ali izbere samo oglase za nakup oziroma prodajo.
Podroben ogled posameznega oglasa: S pomočjo ID-ja lahko uporabnik pridobi podrobne informacije o izbranem oglasu.
Oddaja oglasa s samodejnim ujemanjem: Ob objavi novega oglasa sistem samodejno poišče in prikaže nasprotne oglase, ki se ujemajo po kategoriji in ključni besedi iz naslova.

##Baza:
Baza je sestavljena iz treh tabel.

Tabela uporabnik:
Hrani osnovne podatke o uporabnikih.
id – primarni ključ
ime, priimek, email

Tabela kategorija:
Vsebuje vnaprej določen seznam kategorij (npr. Elektronika, Obutev).
id – primarni ključ
naziv – ime kategorije

Tabela oglas:
Glavna tabela z oglasi.
id – primarni ključ
naslov – naslov oglasa (npr. črni čevlji)
opis – podrobnejši opis izdelka
cena – pričakovana ali zahtevana cena
tip – določa, ali gre za nakup ali prodajo
uporabnik_id – tuji ključ na tabelo uporabnik
kategorija_id – tuji ključ na tabelo kategorija

##ER diagram:
Uporabnik je v relaciji 1 : N z oglasom, saj lahko objavi več oglasov. Oglas pripada eni kategoriji, kategorija pa lahko vsebuje več oglasov.

  <img width="909" height="488" alt="UPORABNIK (1)" src="https://github.com/user-attachments/assets/20ec97ae-279b-45f6-949a-8b9bcb5edace" />
