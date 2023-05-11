#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *
import sqlite3

# uvozimo ustrezne podatke za povezavo

from Data.model import *
from Database import Repo

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
def stranke():
    cur.execute("""
      SELECT id_stranka, ime_priimek, telefon, mail from Stranka
    """)
    return bottle.template('stranke.html', stranke=cur)


@get('/dodaj_stranko')
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
      with povpr as (select ime_priimek, round(avg(ocena),2) povprecna_ocena
        from Ocena
        group by ime_priimek) 
        select u.*, p.povprecna_ocena
        from usluzbenec u
        left join povpr p on p.ime_priimek = u.ime_priimek;
    """)

    return bottle.template('usluzbenci.html', usluzbenci=cur)


@get('/dodaj_usluzbenca')
def dodaj_usluzbenca_get():
    return bottle.template('dodaj_usluzbenca.html', ime_priimek='', napake=None)

@post('/dodaj_usluzbenca')
def dodaj_usluzbenca_post():
  ime_priimek = request.forms.ime_priimek
  ime_storitve = request.forms.ime_storitve
#  try:
  cur.execute("""
      INSERT INTO Usluzbenec (ime_priimek)
      VALUES (%s) RETURNING id_usluzbenec; 
    """, (ime_priimek)
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
def dodaj_oceno(id_usluzbenec):
    cur.execute("""SELECT  
                    u.ime_priimek
                    FROM Usluzbenec u
                    WHERE u.id_usluzbenec = %s""", [id_usluzbenec])
    return template('dodaj_oceno.html', id_usluzbenec = id_usluzbenec, ime_priimek=cur.fetchone()[0], ocena='', napaka=None)


@post('/dodaj_oceno')
def dodaj_oceno_post():
    ime_priimek = request.forms.get("ime_priimek")
    ocena = int(request.forms.get("ocena"))

    cur.execute("""
      INSERT INTO Ocena (ime_priimek, ocena)
      VALUES (%s, %s) RETURNING id_ocena; 
    """, (ime_priimek, ocena)
        )
    conn.commit()
    redirect(url('/'))

# drugi način: da ni treba vpisat ime_priimek ampak klikneš na + in samo dodas oceno temu uslužbencu (ne dela nevem zakaj)
# @get('/dodaj_oceno/<ime_priimek:str>')
# def dodaj_oceno_get(ime_priimek):   
#     return template('dodaj_oceno_2.html', ime_priimek=ime_priimek, ocena='', napaka=None)


# @post('/dodaj_oceno/<ime_priimek:str>')
# def dodaj_oceno_post(ime_priimek):
#     ime_priimek = Usluzbenec.ime_priimek
#     ocena = request.forms.ocena
# #    try:
#     cur.execute("INSERT INTO Ocena (id_usluzbenec, ocena) VALUES (%s, %s)",
#                 (ime_priimek, ocena)
#                 )
#     conn.commit()
#    except Exception as ex:
#        conn.rollback()
#        return template('dodaj_oceno.html', ime_priimek=ime_priimek, ocena=ocena,
#                        napaka='Zgodila se je napaka: %s' % ex)
#    redirect(url('index'))

### STORITVE
@get('/dodaj_storitev')
def dodaj_storitev():
    
    return template('dodaj_storitev.html', ime_priimek='', storitev='', napaka=None)


@post('/dodaj_storitev')
def dodaj_storitev_post():
    ime_priimek = request.forms.ime_priimek
    storitev = request.forms.storitev
    try:
        cur.execute("INSERT INTO Usluzb_storitve (ime_priimek, storitev) VALUES (%s, %s)",
                    (ime_priimek, storitev))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_storitev.html', ime_priimek=ime_priimek, storitev=storitev,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/'))

@get('/storitev_usluzbenci_get/<id_storitev:int>')
def storitev_usluzbenci_get(id_storitev):
    cur.execute("""SELECT  
                    u.id_usluzbenec, u.ime_priimek
                    FROM Storitev s
                    left JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
                    left JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
                    WHERE s.id_storitev = %s""", [id_storitev])
    return template('storitev_usluzbenci.html', id_storitev=id_storitev, usluzbenci=cur)


@get('/termin')
def vpis_termina_get():
    pass

@post('/termin')
def vpis_termina_post():
    ime_priimek_stranke = request.forms.ime_priimek_stranke
    datum = request.forms.datum
    ime_storitve = request.forms.ime_storitve
    ime_priimek_usluzbenca = request.forms.ime_priimek_usluzbenca
    koda = request.forms.koda
    #cur = baza.cursor
    cur.execute("""
    """)


######################################################################
# Glavni program




# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
#if __name__ == "__main__":
#    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

@bottle.error(404)
def error_404(error):
    return "Ta stran ne obstaja!"

bottle.run(reload=True, debug=True)