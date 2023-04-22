#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import get, post, run, request, template, redirect, static_file, url

# uvozimo ustrezne podatke za povezavo

from Data.Database import Repo
from Data.model import *


import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah
# debug(True)

repo = Repo()

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
def index():
   'Začetna stran'

@get('/stranke')
def stranke():
    stranke = repo.tabela_stranka()
    return template('stranke.html', stranke=stranke)

#Treba je bolj pogledati html od gašperja, ker nevem kako bi to zagnala da mi pokaže tabelo,
#mogoče bi blo bolje, da bi gledale od janoša datoteko https://github.com/jaanos/OPB/blob/master/predavanja/primeri/banka/banka.py,
#ker se mi zdi, da ni tako komlicirano kot tukaj... in tudi html-ji so lažji


#@get('/dodaj_stranko')
#def dodaj_stranko():
    
   # return template('dodaj_stranko.html', stranka = Stranka())


######################################################################
# Glavni program



# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)