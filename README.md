# BolhaSmart

## Namen:
Namen projekta je ustvariti aplikacijo za prodajo in nakup rabljenih predmetov. Uporabnik lahko odda oglas za nakup ali prodajo, aplikacija pa mu samodejno vrne oglase nasprotnega tipa, ki se ujemajo glede na kategorijo in ključne besede v naslovu.

## Funkcionalnosti:
Pregled vseh oglasov: Uporabniku se izpišejo vsi oglasi za nakup in prodajo.\
Brskanje po kategorijah: Uporabnik izbere kategorijo, aplikacija pa prikaže ustrezne oglase.\
Iskanje po ključnih besedah: Oglase je mogoče filtrirati glede na besedo, ki se pojavi v naslovu oglasa.\
Filtriranje po tipu: Uporabnik lahko izbere samo oglase za nakup oziroma prodajo.\
Podroben ogled posameznega oglasa: S pomočjo ID-ja lahko uporabnik pridobi podrobne informacije o izbranem oglasu.\
Oddaja oglasa s samodejnim ujemanjem: Ob objavi novega oglasa sistem samodejno poišče in prikaže nasprotne oglase, ki se ujemajo po kategoriji in ključni besedi iz naslova.

## Baza:
Baza je sestavljena iz treh tabel.

Tabela uporabnik – hrani osnovne podatke o uporabnikih:
* `id` – primarni ključ
* `ime`, `priimek`
* `email` – naslov za prijavo
* `geslo` – bcrypt zgostitev gesla
* `admin` – oznaka administratorja (0/1)

Tabela kategorija – vsebuje vnaprej določen seznam kategorij (npr. Elektronika, Obutev):
* `id` – primarni ključ
* `naziv` – ime kategorije

Tabela oglas – glavna tabela z oglasi:
* `id` – primarni ključ
* `naslov` – naslov oglasa, obvezen (npr. črni čevlji)
* `opis` – podrobnejši opis izdelka
* `cena` – pričakovana ali zahtevana cena; lahko manjka ("po dogovoru")
* `tip` – določa, ali gre za nakup ali prodajo (obvezen)
* `uporabnik_id` – tuji ključ na tabelo uporabnik
* `kategorija_id` – tuji ključ na tabelo kategorija

## ER diagram:
Uporabnik je v relaciji 1 : N z oglasom, saj lahko objavi več oglasov. Oglas pripada eni kategoriji, kategorija pa lahko vsebuje več oglasov.

  <img width="909" height="488" alt="UPORABNIK (1)" src="https://github.com/user-attachments/assets/20ec97ae-279b-45f6-949a-8b9bcb5edace" />

## Zagon:
Aplikacija se nahaja v imeniku `BolhaSmart`, ki ni korenski imenik repozitorija, zato se je treba najprej premakniti vanj.

1. Premakni se v imenik: `cd BolhaSmart`
2. Namesti knjižnjico bcrypt: `pip install bcrypt`
3. Poženi bazo: `python baza.py`
4. Zaženi aplikacijo: `python spletni_vmesnik.py`
5. Odpri brskalnik na: `http://127.0.0.1:8080/`

## Prijavni podatki za testiranje:
* Navaden uporabnik: `marko.horvat2@example.com` / geslo `test123`
* Administrator: `admin@bolha.si` / geslo `admin123` (lahko ureja in briše katerikoli oglas)
