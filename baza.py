import sqlite3 as dbapi
import csv

BAZA = "moja_baza.db"

def uvozi_skripto(skripta, baza): 
    """Naredimo tabele: uporabnik, oglas in kategorija"""
    try:
        conn = dbapi.connect(baza)
        cur = conn.cursor()
        with open(skripta) as f:
            with conn:
                cur.executescript(f.read())
        
    finally:
        conn.close()

def uvozi_uporabnike(baza, csv_datoteka):
    """Uvozimo podatke v tabela uporabnik iz datoteke uporabnik.csv"""
    try:
        conn = dbapi.connect(baza)
        with open(csv_datoteka, encoding='utf-8') as f:
            rd = csv.reader(f)
            next(rd)
            uporabniki = list(rd)
        with conn:
            cur = conn.cursor()
            cur.executemany("INSERT INTO uporabnik (ime, priimek, email) VALUES (?, ?, ?)", uporabniki)
        
    finally:
        conn.close()


def uvozi_kategorije(baza, csv_datoteka):
    """Uvozimo podatke v tabela kategorija iz datoteke kategorija.csv"""
    try:
        conn = dbapi.connect(baza)
        with open(csv_datoteka, encoding='utf-8') as f:
            rd = csv.reader(f)
            next(rd)
            kategorije = list(rd)
        with conn:
            cur = conn.cursor()
            cur.executemany("INSERT INTO kategorija (naziv) VALUES (?)", kategorije)

        
    finally:
        conn.close()


def uvozi_oglase(baza, csv_datoteka):
    """Uvozimo podatke v tabela oglas iz datoteke oglas.csv"""
    try:
        conn = dbapi.connect(baza)
        with open(csv_datoteka, encoding='utf-8') as f:
            rd = csv.reader(f)
            next(rd)
            oglasi = list(rd)
        with conn:
            cur = conn.cursor()
            cur.executemany("INSERT INTO oglas (naslov, opis, cena, tip, uporabnik_id, kategorija_id) VALUES (?, ?, ?, ?, ?, ?)", oglasi)
        
    finally:
        conn.close()

if __name__ == "__main__":
    uvozi_skripto('shema.sql', BAZA)
    uvozi_uporabnike(BAZA, 'podatki/uporabnik.csv')
    uvozi_kategorije(BAZA, 'podatki/kategorija.csv')
    uvozi_oglase(BAZA, 'podatki/oglas.csv')

