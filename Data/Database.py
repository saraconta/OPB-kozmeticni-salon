# uvozimo psycopg2
#import psycopg2, psycopg2.extensions, psycopg2.extras
#psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

from typing import List
from Data.model import * #uvozimo classe tabel

import Data.auth as auth #uvozimo za delo z bazo
from datetime import date


class Repo:

    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    

    def Stranke(self) -> Stranka: 
        stranke = self.cur.execute(
            """
            SELECT s.id_stranka, s.ime_priimek, s.telefon, s.mail FROM Stranka s
            """)

        return [Stranka(id_stranka, ime_priimek, telefon, mail) for (id_stranka, ime_priimek, telefon, mail) in stranke]

    def dobi_stranko(self, ime: str) -> Stranka:
        # Preverimo, če stranka že obstaja
        self.cur.execute("""
            SELECT id_stranka, ime_priimek, telefon, mail from Stranka
            WHERE ime_priimek = %s
          """, (ime,))
        
        row = self.cur.fetchone()

        if row:
            id_stranka, ime_priimek, telefon, mail = row
            return Stranka(id_stranka, ime_priimek, telefon, mail)
        
        raise Exception("Stranka z imenom " + ime + " ne obstaja")

    
    def dodaj_stranko(self, stranka: Stranka) -> Stranka:

        # Preverimo, če stranka že obstaja
        self.cur.execute("""
            SELECT id_stranka, ime_priimek, telefon, mail from Stranka
            WHERE ime_priimek = %s
          """, (stranka.ime_priimek,))
        
        row = self.cur.fetchone()
        if row:
            stranka.id_stranka = row[0]
            return stranka

        
    

        # Sedaj dodamo stranko
        self.cur.execute("""
            INSERT INTO Stranka (ime_priimek, telefon, mail)
              VALUES (%s, %s, %s) RETURNING id_stranka; """, (stranka.ime_priimek, stranka.telefon, stranka.mail))
        stranka.id_stranka = self.cur.fetchone()[0]
        self.conn.commit()
        return stranka

#še funkcijo za izbrisi_stranko ?? ali to ne bi? Da ko je bila enkrat pri nas 
# oziroma se je vpisala v našo bazo, tam ostane za vedno??

    def dobi_storitev(self, ime: str) -> Storitev:
        # Preverimo, če storitev že obstaja
        self.cur.execute("""
            SELECT id_storitev, ime_storitve, trajanje, cena, stroski from Storitev
            WHERE ime_storitve = %s
          """, (ime,))
        
        row = self.cur.fetchone()

        if row:
            id_storitev, ime_storitve, trajanje, cena, stroski = row
            return Storitev(id_storitev, ime_storitve, trajanje, cena, stroski)
        
        raise Exception("Storitev z imenom " + ime + " ni v ponudbi")


    def dodaj_storitev(self, storitev: Storitev) -> Storitev:

        # Preverimo, če storitev že obstaja
        self.cur.execute("""
            SELECT id_storitev, ime_storitve, trajanje, cena, stroski from Storitev
            WHERE ime_storitve = %s
          """, (storitev.ime_storitve,))
        
        row = self.cur.fetchone()
        if row:
            storitev.id_storitev = row[0]
            return storitev


        # Sedaj dodamo storitev
        self.cur.execute("""
            INSERT INTO Storitev (ime_storitve, trajanje, cena, stroski)
              VALUES (%s, %s, %s, %s) RETURNING id_storitev; """, 
              (storitev.ime_storitve, storitev.trajanje, storitev.cena, storitev.stroski ))
        storitev.id_storitev = self.cur.fetchone()[0]
        self.conn.commit()
        return storitev



















    