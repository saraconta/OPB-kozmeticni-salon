#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *
import sqlite3

# uvozimo ustrezne podatke za povezavo

from Data.model import *
from Database import Repo

# from Data.services import AuthService
# from functools import wraps

import os
import bottle


import Data.auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# odkomentiraj, če želiš sporočila o napakah
# debug(True)

repo = Repo()


# auth = AuthService(repo)

# def cookie_required(f):
#     """
#     Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
#     """
#     @wraps(f)
#     def decorated( *args, **kwargs):


#         cookie = request.get_cookie("uporabnik")
#         if cookie:
#             return f(*args, **kwargs)

#         return template("prijava.html", napaka="Potrebna je prijava!")




#     return decorated


#@get('/static/<filename:path>')
#def static(filename):
#    return static_file(filename, root='static')

@get('/')
def index():
   cur.execute("""
      SELECT id_storitev, ime_storitve, cena from Storitev
   """)
   return bottle.template('zacetna_stran.html', storitve=cur)

### STRANKE
@get('/stranke')
# @cookie_required
def stranke():
    cur.execute("""
      SELECT id_stranka, ime_priimek, telefon, mail from Stranka
    """)
    return bottle.template('stranke.html', stranke=cur)


@get('/dodaj_stranko')
#@cookie_required
def dodaj_stranko():
    return template('dodaj_stranko.html', ime_priimek='', telefon='', mail='', napake=None)

@post('/dodaj_stranko')
def dodaj_stranko_post():
  ime_priimek = request.forms.ime_priimek
  telefon = request.forms.telefon
  mail = request.forms.mail
  cur.execute("""
      INSERT INTO Stranka (ime_priimek, telefon, mail)
      VALUES (%s, %s, %s) RETURNING id_stranka; 
    """, (ime_priimek, telefon, mail)
    )
  conn.commit()
  redirect(url('/'))

### USLUŽBENCI
@get('/usluzbenci')
def usluzbenci():
    cur.execute("""
        WITH povpr AS (SELECT ime_priimek, round(avg(ocena),2) povprecna_ocena
          FROM Ocena
          GROUP BY ime_priimek) 
        SELECT u.*, p.povprecna_ocena
        FROM usluzbenec u
        LEFT JOIN povpr p ON p.ime_priimek = u.ime_priimek;
      """)
    return bottle.template('usluzbenci.html', usluzbenci=cur)


@get('/dodaj_usluzbenca')
#@cookie_required
def dodaj_usluzbenca_get():
    return bottle.template('dodaj_usluzbenca.html', ime_priimek='', storitev='', napake=None)

@post('/dodaj_usluzbenca')
def dodaj_usluzbenca_post():
  ime_priimek = request.forms.ime_priimek
  storitev = request.forms.storitev
#  try:
  cur.execute("""
      with ins1 as(
      INSERT INTO Usluzbenec (ime_priimek) VALUES (%s) RETURNING id_usluzbenec
      )
      INSERT INTO Usluzb_storitve (id_usluzbenec, ime_storitve)
      SELECT id_usluzbenec, %s FROM ins1;

    """, (ime_priimek, storitev)
    )
  conn.commit()

  redirect(url('/'))
#  except Exception as ex:
#    conn.rollback()
#    return template('dodaj_usluzbenca.html', ime_priimek=ime_priimek, ime_storitve=ime_storitve,
#      napaka='Zgodila se je napaka: %s' % ex)
#  redirect(url('index'))
#mogli bi še preverit: ali je storitev na ceniku ter ali ta usluzbenec že obstaja


### OCENE
@get('/dodaj_oceno/<id_usluzbenec:int>')
#@cookie_required
def dodaj_oceno(id_usluzbenec):
    cur.execute("""SELECT  
                    u.ime_priimek
                    FROM Usluzbenec u
                    WHERE u.id_usluzbenec = %s""", [id_usluzbenec])
    return template('dodaj_oceno.html', id_usluzbenec = id_usluzbenec, ime_priimek=cur.fetchone()[0], ocena='', napaka=None)

@post('/dodaj_oceno/<id_usluzbenec:int>')
def dodaj_oceno_post(id_usluzbenec):
    cur.execute("""SELECT  
                    u.ime_priimek
                    FROM Usluzbenec u
                    WHERE u.id_usluzbenec = %s""", [id_usluzbenec])
    ime_priimek = cur.fetchone()[0]
    ocena = int(request.forms.get("ocena"))

    cur.execute("""
      INSERT INTO Ocena (ime_priimek, ocena)
      VALUES (%s, %s) RETURNING id_ocena; 
    """, (ime_priimek, ocena)
        )
    conn.commit()
    redirect(url('/'))


### STORITVE
@get('/dodaj_storitev')
#@cookie_required
def dodaj_storitev():  
    return template('dodaj_storitev.html', ime_priimek='', storitev='', napaka=None)


@post('/dodaj_storitev')
def dodaj_storitev_post():
    ime_priimek = request.forms.ime_priimek
    storitev = request.forms.storitev

    try:
      cur.execute("""
      with view1 as(
      SELECT id_usluzbenec FROM Usluzbenec WHERE ime_priimek = %s
      )
      INSERT INTO Usluzb_storitve (id_usluzbenec, ime_storitve)
      SELECT id_usluzbenec, %s FROM view1;

    """, (ime_priimek, storitev)
    )
      conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_storitev.html', ime_priimek=ime_priimek, storitev=storitev,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/'))


@get('/storitev_usluzbenci_get/<id_storitev:int>')
def storitev_usluzbenci_get(id_storitev):
    cur.execute("""
      SELECT u.id_usluzbenec, u.ime_priimek
      FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
      WHERE s.id_storitev = %s""", [id_storitev])
    return template('storitev_usluzbenci.html', id_storitev=id_storitev, usluzbenci=cur)


### TERMIN
@get('/termin')
#@cookie_required
def termina_storitev():
    cur.execute("""
      SELECT id_storitev, ime_storitve FROM Storitev
    """)
    return bottle.template('termin_storitev.html', storitve=cur)

  
@get('/termin/<id_storitev:int>')
#@cookie_required
def termina_usluzbenec(id_storitev):
    cur.execute("""
      SELECT u.id_usluzbenec, u.ime_priimek
      FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
      WHERE s.id_storitev = %s""", [id_storitev])
    return template('termin_usluzbenec.html', id_storitev = id_storitev, usluzbenci_storitve=cur)

@get('/termin/<id_storitev:int>/<id_usluzbenec:int>')
#@cookie_required
def termin_datum(id_usluzbenec, id_storitev):
    cur.execute("""
      SELECT u.ime_priimek, s.ime_storitve, s.trajanje, u.id_usluzbenec, s.id_storitev
      FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
      WHERE (u.id_usluzbenec, s.id_storitev) = (%s, %s)""", (id_usluzbenec, id_storitev))
    vrstica=cur.fetchone()
    return template('termin.html', id_storitev = id_storitev, id_usluzbenec = id_usluzbenec, 
      ime_priimek_usluzbenca=vrstica[0], ime_storitve=vrstica[1],
      ime_priimek_stranke='', datum='', koda='', napaka=None)

@post('/termin/<id_storitev:int>/<id_usluzbenec:int>')
def vpis_termina_post(id_usluzbenec, id_storitev):
    cur.execute("""
      SELECT u.ime_priimek, s.ime_storitve, s.trajanje, u.id_usluzbenec, s.id_storitev
      FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
      WHERE (u.id_usluzbenec, s.id_storitev) = (%s, %s)""", (id_usluzbenec, id_storitev))
    
    vrstica=cur.fetchone()
    ime_priimek_stranke = request.forms.ime_priimek_stranke
    datum = request.forms.datum
    ura = request.forms.ura
    datum_ura = datum + " " + ura
    ime_storitve = vrstica[1]
    ime_priimek_usluzbenca = vrstica[0]
    koda = request.forms.koda
    #cur = baza.cursor
    cur.execute("""
      INSERT INTO Termin1 (ime_priimek_stranke, datum, ime_storitve, ime_priimek_usluzbenca, koda)
      VALUES (%s, %s, %s, %s, %s) RETURNING id_termin; 
      """, (ime_priimek_stranke, datum_ura, ime_storitve, ime_priimek_usluzbenca, koda)
      )
    conn.commit()
    redirect(url('/'))


######################################################################
# Glavni program




# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
#if __name__ == "__main__":
#    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

@bottle.error(404)
def error_404(error):
    return "Ta stran ne obstaja!"

bottle.run(reload=True, debug=True)