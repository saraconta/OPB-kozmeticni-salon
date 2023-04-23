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

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah
# debug(True)

repo = Repo()

#@get('/static/<filename:path>')
#def static(filename):
#    return static_file(filename, root='static')

@get('/')
def index():
   return bottle.template('zacetna_stran.html')

@get('/stranke')
def stranke():
    stranke = repo.tabela_stranka()
    return bottle.template('stranke.html', stranke=stranke)

#@get('/stranke')
#def stranke(cur):
#    cur.execute(""""
#      SELECT id_stranka, ime_priimek, telefon, mail from Stranka
#    """)
#    return bottle.template('stranke.html', stranke=cur)

#@get('/dodaj_stranko')
#def dodaj_stranko():
    
   # return template('dodaj_stranko.html', stranka = Stranka())


######################################################################
# Glavni program



# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
#if __name__ == "__main__":
#    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

@bottle.error(404)
def error_404(error):
    return "Ta stran ne obstaja!"

bottle.run(reload=True, debug=True)