#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *
import sqlite3

# uvozimo ustrezne podatke za povezavo
from Data.model import *
import Data.auth as auth

from functools import wraps
from datetime import date

import os
import hashlib

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

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

#za cookieje
from functools import wraps


skrivnost = "ns86uffdDS3LE0u2"

def nastaviSporocilo(sporocilo = None):
    staro = request.get_cookie('sporocilo', secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo')
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro 


def cookie_required_up_ime(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("up_ime", secret=skrivnost)
        if cookie:
            return f(*args, **kwargs)
        return template("prijava.html")
    return decorated


def cookie_required_vloga(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("rola", secret=skrivnost)
        if cookie:
            return f(*args, **kwargs)
        return template("prijava.html")
    return decorated

######################################################################################################
### REGISTRACIJA IN PRIJAVA

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


@get('/registracija_stranka')
def registracija_stranka():
    napaka = nastaviSporocilo()
    return template('registracija_stranka.html', napaka=napaka)


@post('/registracija_stranka')
def registracija_stranka_post():
    ime_priimek = request.forms.ime_priimek
    up_ime = request.forms.up_ime
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2

    if ime_priimek is None or up_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Registracija ni mogoča!') 
        redirect(url('registracija_stranka'))
        return    
    uporabnik = None
    try: 
        cur.execute("""
            SELECT id_stranka, ime_priimek, telefon, mail, up_ime, admin, geslo
            FROM Stranka WHERE ime_priimek = %s;""", (ime_priimek, ))
        uporabnik = cur.fetchone()
        conn.commit()
    except:
        uporabnik = None
    if uporabnik is None:
        nastaviSporocilo('Registracija ni mogoča!') 
        redirect(url('registracija_stranka'))
        return
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata!') 
        redirect(url('registracija_stranka'))
        return
    
    zgostitev = hashGesla(geslo)

    cur.execute("""
        UPDATE Stranka SET up_ime = %s, geslo = %s 
        WHERE ime_priimek = %s""", (up_ime, zgostitev, ime_priimek))
    
    conn.commit()
    response.set_cookie('up_ime', up_ime, secret=skrivnost)
    redirect(url('prijava'))


@get('/registracija_usluzbenec')
def registracija_usluzbenec():
    napaka = nastaviSporocilo()
    return template('registracija_usluzbenec.html', napaka=napaka)


@post('/registracija_usluzbenec')
def registracija_usluzbenec_post():
    ime_priimek = request.forms.ime_priimek
    up_ime = request.forms.up_ime
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2

    if ime_priimek is None or up_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Registracija ni mogoča!') 
        redirect(url('registracija_usluzbenec'))
        return    
    uporabnik = None
    try: 
        cur.execute("""
            SELECT id_usluzbenec, ime_priimek, up_ime, admin, geslo
            FROM Usluzbenec WHERE ime_priimek = %s;
            """, (ime_priimek, ))
        conn.commit()
        uporabnik = cur.fetchone()
    except:
        uporabnik = None
    if uporabnik is None:
        nastaviSporocilo('Registracija ni mogoča!') 
        redirect(url('registracija_usluzbenec'))
        return
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata!') 
        redirect(url('registracija_usluzbenec'))
        return
    
    zgostitev = hashGesla(geslo)
    cur.execute("""UPDATE Usluzbenec SET up_ime = %s, geslo = %s WHERE ime_priimek = %s;""", (up_ime, zgostitev, ime_priimek))
    conn.commit()
    response.set_cookie('up_ime', up_ime, secret=skrivnost)
    redirect(url('prijava'))


@get('/prijava_stranka')
def prijava_stranka():
    napaka = nastaviSporocilo()
    return template('prijava_stranka.html', napaka=napaka)


@post('/prijava_stranka')
def prijava_stranka_post():
    up_ime = request.forms.up_ime
    geslo = request.forms.geslo

    if up_ime is None or geslo is None:
        nastaviSporocilo('Uporabniško ime in geslo morata biti neprazna!') 
        redirect(url('prijava_stranka'))
        return 
    hashBaza = None
    try: 
        cur.execute("""SELECT geslo FROM Stranka WHERE up_ime = %s""", [up_ime])
        hashBaza = cur.fetchone()[0]
        conn.commit()
    except:
        hashBaza = None
    if hashBaza is None:
        nastaviSporocilo('Uporabniško ime oziroma geslo nista ustrezna!') 
        redirect(url('prijava_stranka'))
        return print('Uporabniško ime oziroma geslo nista ustrezna!')
    if hashGesla(geslo) != hashBaza:
        nastaviSporocilo('Uporabniško ime oziroma geslo nista ustrezna!') 
        redirect(url('prijava_stranka'))
        return
    
    response.set_cookie('up_ime', up_ime, secret=skrivnost)
    response.set_cookie('rola', 'stranka', secret=skrivnost)
    redirect(url('zacetek'))


@get('/prijava_usluzbenec')
def prijava_usluzbenec():
    napaka = nastaviSporocilo()
    return template('prijava_usluzbenec.html', napaka=napaka)


@post('/prijava_usluzbenec')
def prijava_usluzbenec_post():
    up_ime = request.forms.up_ime
    geslo = request.forms.geslo

    if up_ime is None or geslo is None:
        nastaviSporocilo('Uporabniško ime in geslo morata biti neprazna!') 
        redirect(url('prijava_usluzbenec'))
        return
    hashBaza = None
    try: 
        cur.execute("""SELECT geslo FROM Usluzbenec WHERE up_ime = %s;""", [up_ime])
        hashBaza = cur.fetchone()[0]
        conn.commit()
    except:
        hashBaza = None
        print("baza je None")
    if hashBaza is None:
        nastaviSporocilo('Uporabniško ime oziroma geslo nista ustrezna!') 
        redirect(url('prijava_usluzbenec'))
        return 
    if hashGesla(geslo) != hashBaza:
        nastaviSporocilo('Uporabniško ime oziroma geslo nista ustrezna!') 
        redirect(url('prijava_usluzbenec'))
        return
    
    response.set_cookie('up_ime', up_ime, secret=skrivnost)
    response.set_cookie('rola', 'usluzbenec', secret=skrivnost)
    redirect(url('zacetek'))
    

@get('/prijava')
def prijava():
    napaka = nastaviSporocilo()

    return template('prijava.html', napaka=napaka)


@get('/odjava')
@cookie_required_up_ime
@cookie_required_vloga
def odjava():
    response.delete_cookie('up_ime')
    response.delete_cookie('rola')

    return template('prijava.html', napaka=None)
  

#################################################################################
### ZAČETNA STRAN

@get('/') 
def index():
  return template('dobrodosli.html',napaka=None)


@get('/zacetek')
@cookie_required_up_ime
@cookie_required_vloga
def zacetek():
  up_ime = request.get_cookie('up_ime', secret=skrivnost)
  vloga = request.get_cookie('rola', secret=skrivnost)

  if vloga == 'usluzbenec':
    cur.execute("""
        SELECT admin FROM Usluzbenec 
            WHERE up_ime = %s;
    """, [up_ime])
    ali_je_sef = cur.fetchone()[0]

  else:
    ali_je_sef = None

  cur.execute("""
     SELECT id_storitev, ime_storitve, cena FROM Storitev
  """)

  podnaslov = 'Pozdravljeni' + ' ' + up_ime + '.'

  return template('zacetna_stran.html', storitve=cur, up_ime=up_ime, podnaslov=podnaslov,
    vloga=vloga, ali_je_sef=ali_je_sef) 


################################################################################################
### STRANKE

@get('/stranke')
@cookie_required_up_ime
@cookie_required_vloga
def stranke():
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]

        cur.execute("""
            SELECT id_stranka, ime_priimek, telefon, mail FROM Stranka;
        """)

    else:
        ali_je_sef = None
        cur.execute("""
            SELECT id_stranka, ime_priimek, telefon, mail FROM Stranka WHERE up_ime = %s;
        """, [up_ime])
        
    return template('stranke.html', stranke=cur, vloga=vloga, ali_je_sef=ali_je_sef)


@get('/vpis_stranke_v_bazo')
def vpis_stranke_v_bazo():
    return template('vpis_stranke_v_bazo.html', ime_priimek='', telefon='', mail='', napake=None)


@post('/vpis_stranke_v_bazo')
def vpis_stranke_v_bazo_post():
  ime_priimek = request.forms.ime_priimek
  telefon = request.forms.telefon
  mail = request.forms.mail

  try:
    cur.execute("""
        INSERT INTO Stranka (ime_priimek, telefon, mail)
        VALUES (%s, %s, %s) RETURNING id_stranka; 
    """, (ime_priimek, telefon, mail))
    conn.commit()

  except Exception as ex:
    conn.rollback()
    return template('dodaj_stranko.html', ime_priimek=ime_priimek, telefon=telefon, mail=mail,
        napaka='Zgodila se je napaka: (%s, %s, %s)' % ex)
  
  redirect(url('prijava'))


@get('/dodaj_stranko')
@cookie_required_up_ime
@cookie_required_vloga
def dodaj_stranko():
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]

    else:
        ali_je_sef = None

    return template('dodaj_stranko.html', ime_priimek='', telefon='', mail='', napake=None,
                    ali_je_sef = ali_je_sef)


@post('/dodaj_stranko')
def dodaj_stranko_post():
  ime_priimek = request.forms.ime_priimek
  telefon = request.forms.telefon
  mail = request.forms.mail

  try:
    cur.execute("""
        INSERT INTO Stranka (ime_priimek, telefon, mail)
        VALUES (%s, %s, %s) RETURNING id_stranka; 
    """, (ime_priimek, telefon, mail))
    conn.commit()

  except Exception as ex:
    conn.rollback()
    return template('dodaj_stranko.html', ime_priimek=ime_priimek, telefon=telefon, mail=mail,
        napaka='Zgodila se je napaka: (%s, %s, %s)' % ex)
  
  redirect(url('zacetek'))


##################################################################################################
### USLUŽBENCI

@get('/usluzbenci')
@cookie_required_up_ime
@cookie_required_vloga
def usluzbenci():
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]

    else:
        ali_je_sef = None

    cur.execute("""
        WITH povpr AS (SELECT ime_priimek, round(avg(ocena),2) povprecna_ocena
            FROM Ocena
            GROUP BY ime_priimek) 
        SELECT u.id_usluzbenec, u.ime_priimek, p.povprecna_ocena
        FROM usluzbenec u 
        LEFT JOIN povpr p ON p.ime_priimek = u.ime_priimek
        order by u.ime_priimek asc;
    """)

    return template('usluzbenci.html', usluzbenci=cur, ali_je_sef=ali_je_sef, vloga=vloga)


@get('/dodaj_usluzbenca')   #dodaja lahko samo šefica: up_ime = clarisa
@cookie_required_up_ime
@cookie_required_vloga
def dodaj_usluzbenca_get():
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
            WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]

    else:
        ali_je_sef = None

    return template('dodaj_usluzbenca.html', ime_priimek='', storitev='', ali_je_sef=ali_je_sef, napake=None)


@post('/dodaj_usluzbenca')
def dodaj_usluzbenca_post():
  ime_priimek = request.forms.ime_priimek
  storitev = request.forms.storitev

  try:
      cur.execute("""
        with ins1 as(
            INSERT INTO Usluzbenec (ime_priimek) VALUES (%s) RETURNING id_usluzbenec
        )
        INSERT INTO Usluzb_storitve (id_usluzbenec, ime_storitve)
        SELECT id_usluzbenec, %s FROM ins1;
        """, (ime_priimek, storitev))
      conn.commit()

  except Exception as ex:
      conn.rollback()
      return template('dodaj_usluzbenca.html', ime_priimek=ime_priimek, storitev=storitev,
        napaka='Zgodila se je napaka: %s' % ex)
  
  redirect(url('usluzbenci'))


###############################################################################################
### OCENE

@get('/dodaj_oceno/<id_usluzbenec:int>') #oceno lahko doda samo stranka
@cookie_required_up_ime
@cookie_required_vloga
def dodaj_oceno(id_usluzbenec):
    vloga = request.get_cookie('rola', secret=skrivnost)  

    cur.execute("""
        SELECT u.ime_priimek
        FROM Usluzbenec u
        WHERE u.id_usluzbenec = %s;
    """, [id_usluzbenec])

    return template('dodaj_oceno.html', id_usluzbenec=id_usluzbenec, ime_priimek=cur.fetchone()[0], ocena='',
        vloga=vloga, napaka=None)


@post('/dodaj_oceno/<id_usluzbenec:int>')
def dodaj_oceno_post(id_usluzbenec):
    cur.execute("""
        SELECT u.ime_priimek
            FROM Usluzbenec u
            WHERE u.id_usluzbenec = %s;
        """, [id_usluzbenec])
    
    ime_priimek = cur.fetchone()[0]
    ocena = int(request.forms.get("ocena"))

    cur.execute("""
        INSERT INTO Ocena (ime_priimek, ocena)
            VALUES (%s, %s) RETURNING id_ocena; 
        """, (ime_priimek, ocena))
    
    conn.commit()
    redirect(url('usluzbenci'))


@get('/storitve/<id_usluzbenec:int>')
@cookie_required_up_ime
@cookie_required_vloga
def storitve(id_usluzbenec):
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)
    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]
    else:
        ali_je_sef = None

    cur.execute("""
        SELECT u.ime_priimek
            FROM Usluzbenec u
            WHERE u.id_usluzbenec = %s;
        """, [id_usluzbenec])
    
    ime_priimek = cur.fetchone()[0]
    besedilo = 'Storitve, ki jih nudi' + ' ' + ime_priimek 
    cur.execute("""
        SELECT us.ime_storitve ime1, 1 ime2
            FROM Usluzb_storitve us
            WHERE us.id_usluzbenec = %s;
    """, [id_usluzbenec])
    
    return template('storitve.html', id_usluzbenec=id_usluzbenec, storitve=cur, napaka=None,
                    besedilo=besedilo, ali_je_sef=ali_je_sef)


##################################################################################################
### STORITVE

@get('/dodaj_storitev/<id_usluzbenec:int>')  #storitev uslužbencu lahko doda samo šef (clarisa)
@cookie_required_up_ime
@cookie_required_vloga
def dodaj_storitev(id_usluzbenec): 
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]
    else:
        ali_je_sef = None
    cur.execute("""select ime_priimek from Usluzbenec where up_ime = %s;""",[up_ime])
    ime_priimek = cur.fetchone()[0]
    besedilo = 'Dodajanje nove storitve za' + ' ' + ime_priimek
    cur.execute("""
        SELECT u.ime_priimek
            FROM Usluzbenec u
            WHERE u.id_usluzbenec = %s;
    """,[id_usluzbenec])
    
    return template('dodaj_storitev.html', id_usluzbenec=id_usluzbenec,
        ime_priimek=cur.fetchone()[0], storitev='', ali_je_sef=ali_je_sef, napaka=None, besedilo=besedilo)


@post('/dodaj_storitev/<id_usluzbenec:int>')
def dodaj_storitev_post(id_usluzbenec):
  storitev = request.forms.storitev

  cur.execute("""
        INSERT INTO Usluzb_storitve (id_usluzbenec, ime_storitve) VALUES (%s, %s);
    """, (id_usluzbenec, storitev))
  
  conn.commit()
  redirect(url('usluzbenci'))


@get('/storitev_usluzbenci_get/<id_storitev:int>')
@cookie_required_up_ime
@cookie_required_vloga
def storitev_usluzbenci_get(id_storitev):
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)
    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]
    else:
        ali_je_sef = None
    cur.execute("""select ime_storitve from Storitev where id_storitev = %s;""", [id_storitev])
    ime_storitve = cur.fetchone()[0]
    besedilo = 'Uslužbenci, ki nudijo' + ' ' + ime_storitve 
    cur.execute("""
      SELECT u.id_usluzbenec, u.ime_priimek
        FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
        WHERE s.id_storitev = %s;
    """, [id_storitev])

    return template('storitev_usluzbenci.html', id_storitev=id_storitev, usluzbenci=cur, ali_je_sef = ali_je_sef,
                    besedilo = besedilo)


##############################################################################################
### TERMIN

@get('/termin')                 #termin si lahko rezervira samo stranka
@cookie_required_up_ime
@cookie_required_vloga
def termina_storitev():
    vloga = request.get_cookie('rola', secret=skrivnost)    

    cur.execute("""
      SELECT id_storitev, ime_storitve FROM Storitev;
    """)

    return template('termin_storitev.html', storitve=cur, vloga=vloga)

  
@get('/termin/<id_storitev:int>')
@cookie_required_up_ime
@cookie_required_vloga
def termina_usluzbenec(id_storitev):
    cur.execute("""
      SELECT u.id_usluzbenec, u.ime_priimek
        FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
        WHERE s.id_storitev = %s;
    """, [id_storitev])

    return template('termin_usluzbenec.html', id_storitev=id_storitev, usluzbenci_storitve=cur)


@get('/termin/<id_storitev:int>/<id_usluzbenec:int>')
@cookie_required_up_ime
@cookie_required_vloga
def termin_stranka(id_usluzbenec, id_storitev):
    cur.execute("""
      SELECT u.ime_priimek, s.ime_storitve, s.trajanje, u.id_usluzbenec, s.id_storitev
        FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
        WHERE (u.id_usluzbenec, s.id_storitev) = (%s, %s);
    """, (id_usluzbenec, id_storitev))

    vrstica=cur.fetchone()
    today = str(date.today())

    return template('termin.html', id_storitev=id_storitev, id_usluzbenec=id_usluzbenec, 
      ime_priimek_usluzbenca=vrstica[0], ime_storitve=vrstica[1], danes=today, datum='', napaka=None)


@get('/termin/<id_storitev:int>/<id_usluzbenec:int>/')
def termin_date_conversion(id_usluzbenec, id_storitev):
    datum = request.query.datum   #dobimo datum iz urlja
    year = datum[0:4]
    month = datum[5:7]
    day = datum[8:10]
    
    # redirect na termin_ura s pravilno oblikovanim datumom
    return redirect(url('termin_ura', id_usluzbenec=id_usluzbenec, id_storitev=id_storitev, year=year, month=month, day=day))


@get('/termin/<id_storitev:int>/<id_usluzbenec:int>/<year:int>-<month:int>-<day:int>')
@cookie_required_up_ime
@cookie_required_vloga
def termin_ura(id_usluzbenec, id_storitev, year, month, day):
    vloga = request.get_cookie('rola', secret=skrivnost)
    up_ime = request.get_cookie('up_ime', secret=skrivnost)

    if vloga == 'stranka':
        cur.execute("""
            SELECT ime_priimek FROM Stranka 
            WHERE up_ime = %s;
        """, [up_ime])
        ime = cur.fetchone()[0]
    else: 
        ime = None 

    datum = f"{year}-{month}-{day}"  # nastavimo parameter datum

    cur.execute("""
        WITH a AS (
            SELECT t.datum::time zacetek,   t.datum::time + (s.trajanje * interval '1 Minute') konec 
            FROM termin1 t
            LEFT JOIN usluzbenec u ON t.ime_priimek_usluzbenca = u.ime_priimek
            LEFT JOIN storitev s ON t.ime_storitve = s.ime_storitve
            WHERE id_usluzbenec  = %s
            and t.datum::date = %s
        )
        SELECT ur.zacetek, a.konec FROM Ure ur
        LEFT JOIN a ON a.zacetek = ur.zacetek
        WHERE a.zacetek is null;
    """, [id_usluzbenec, datum])

    return template('termin_ura.html', id_storitev=id_storitev, id_usluzbenec=id_usluzbenec,
        datum=datum, year=year, month=month, day=day, ura=cur, ime_priimek_stranke=ime, koda='', napaka=None)


@post('/termin/<id_storitev:int>/<id_usluzbenec:int>/<year:int>-<month:int>-<day:int>')
@cookie_required_up_ime
@cookie_required_vloga
def vpis_termina_post(id_usluzbenec, id_storitev, year, month, day):
    vloga = request.get_cookie('rola', secret=skrivnost)
    up_ime = request.get_cookie('up_ime', secret=skrivnost)

    if vloga == 'stranka':
        cur.execute("""
        SELECT ime_priimek from Stranka 
        WHERE up_ime = %s;
        """, [up_ime])
        ime = cur.fetchone()[0]
    else: 
        ime = None 

    datum = f"{year}-{month}-{day}"

    cur.execute("""
        SELECT u.ime_priimek, s.ime_storitve, s.trajanje, u.id_usluzbenec, s.id_storitev
        FROM Storitev s
        LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
        LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
        WHERE (u.id_usluzbenec, s.id_storitev) = (%s, %s);
    """, (id_usluzbenec, id_storitev))
    
    vrstica=cur.fetchone()
    ime_priimek_stranke = ime
    ura = request.forms.ura
    datum_ura = datum + " " + ura
    ime_storitve = vrstica[1]
    ime_priimek_usluzbenca = vrstica[0]
    koda = request.forms.koda

    cur.execute("""
      INSERT INTO Termin1 (ime_priimek_stranke, datum, ime_storitve, ime_priimek_usluzbenca, koda)
      VALUES (%s, %s, %s, %s, %s) RETURNING id_termin;  
      """, (ime_priimek_stranke, datum_ura, ime_storitve, ime_priimek_usluzbenca, koda))
    
    id_termin = cur.fetchone()[0]
    conn.commit()
    redirect(url('prikazi_termin', id_termin=id_termin))


@get('/prikazi_termin/<id_termin:int>')   #stranka vidi ravnokar rezervirani termin s ceno storitve
@cookie_required_up_ime
@cookie_required_vloga
def prikazi_termin(id_termin):
    cur.execute("""
      SELECT t.id_termin, s.id_stranka, s.ime_priimek, t.datum, t.ime_storitve, t.ime_priimek_usluzbenca, st.trajanje, st.cena, i.popust,
      CASE 
          WHEN i.popust IS NULL THEN cena
          ELSE(1-i.popust) * st.cena 
      END AS koncna_cena
      FROM Termin1 t
      LEFT JOIN Stranka s ON s.ime_priimek = t.ime_priimek_stranke
      LEFT JOIN Storitev st ON st.ime_storitve = t.ime_storitve
      LEFT JOIN Influencer i ON i.koda = t.koda
      WHERE t.id_termin = %s;
    """, [id_termin])

    return template('termin_prikazi.html', id_termin=id_termin, termin=cur)


@get('/pregled_terminov')   #vsaka stranka vidi samo svoje termine, zaposleni vidijo od vseh 
@cookie_required_up_ime
@cookie_required_vloga
def pregled_terminov():
    vloga = request.get_cookie('rola', secret=skrivnost)
    up_ime = request.get_cookie('up_ime', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]

    else:   #če je stranka, vrne samo njen pregled terminov
        ali_je_sef = None
        cur.execute("""
            SELECT id_stranka FROM Stranka 
                WHERE up_ime = %s
        """, [up_ime])
        id_stranka = cur.fetchone()[0]
        return redirect(url('pregled_termina', id_stranka=id_stranka))
    
    cur.execute("""
        SELECT id_stranka, ime_priimek FROM Stranka 
            ORDER BY ime_priimek
    """)

    return template('pregled_terminov.html', stranke=cur, ali_je_sef=ali_je_sef)


@get('/pregled_termina/<id_stranka:int>')  #uslužbenec termina ne sme odstraniti
@cookie_required_up_ime
@cookie_required_vloga
def pregled_termina(id_stranka): 
    vloga = request.get_cookie('rola', secret=skrivnost)
    up_ime = request.get_cookie('up_ime', secret=skrivnost)

    if vloga == 'usluzbenec':
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])
        ali_je_sef = cur.fetchone()[0]

    else: 
        ali_je_sef = None

    cur.execute("""
        SELECT ime_priimek FROM Stranka
        WHERE id_stranka = %s;
    """, [id_stranka])

    ime_priimek = cur.fetchone()[0]
    besedilo = 'Prihodnji rezervirani termini stranke' + ' ' + ime_priimek 
    

    cur.execute("""
        SELECT id_termin, datum, ime_storitve FROM termin1
        LEFT JOIN stranka ON termin1.ime_priimek_stranke = stranka.ime_priimek
        WHERE id_stranka = %s
        AND datum >= CURRENT_TIMESTAMP;
    """, [id_stranka])
    st_vrstic = cur.fetchone()
    return template('pregled_termina.html', tabela=cur, vloga=vloga, ali_je_sef=ali_je_sef, ime_priimek=ime_priimek, besedilo=besedilo, napaka=None,
                    st_vrstic = st_vrstic)

@post('/izbrisi_termin')
def pobrisi_termin():
    id_termin = request.forms.id_termin
    
    cur.execute("""
        DELETE FROM termin1 WHERE id_termin = %s;
    """, [id_termin])

    conn.commit()
    redirect(url('pregled_terminov'))


#########################################################################################
### URNIK

@get('/urnik')
@cookie_required_up_ime
@cookie_required_vloga
def urnik():
    vloga = request.get_cookie('rola', secret=skrivnost)
    up_ime = request.get_cookie('up_ime', secret=skrivnost)

    if vloga == 'usluzbenec': 
        cur.execute("""
            SELECT admin FROM Usluzbenec 
                WHERE up_ime = %s;
        """, [up_ime])

        ali_je_sef = cur.fetchone()[0]

        if ali_je_sef != 2:
            cur.execute("""
                SELECT id_usluzbenec FROM Usluzbenec
                WHERE up_ime = %s;
            """, [up_ime])

            id_usluzbenec = cur.fetchone()[0]

            return redirect(url('prikazi_urnik', id_usluzbenec=id_usluzbenec))
        
    cur.execute("""
      SELECT u.id_usluzbenec, u.ime_priimek FROM usluzbenec u
        ORDER BY ime_priimek;
    """)

    return template('urnik.html', usluzbenci=cur, vloga=vloga, ali_je_sef=ali_je_sef)


@get('/urnik/<id_usluzbenec:int>')
@cookie_required_up_ime
@cookie_required_vloga
def prikazi_urnik(id_usluzbenec):
    vloga = request.get_cookie('rola', secret=skrivnost)
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    if vloga == 'usluzbenec':
      cur.execute("""select admin from Usluzbenec 
          where up_ime = %s""", [up_ime])
      ali_je_sef = cur.fetchone()[0]
    else:
        ali_je_sef = None
    cur.execute("""
        SELECT ime_priimek FROM Usluzbenec
        WHERE id_usluzbenec = %s;
    """, [id_usluzbenec])

    ime_priimek = cur.fetchone()[0]
    besedilo = 'Urnik' + ' ' + ime_priimek + ' ' + 'za prihodnje dni'
    besedilo2 = ime_priimek + ' ' 'v prihodnjih dneh nima naročenih strank.'

    cur.execute("""
        SELECT ime_priimek_stranke, datum, ime_storitve
            FROM Termin1 t
        JOIN Usluzbenec u ON u.ime_priimek = t.ime_priimek_usluzbenca 
            WHERE id_usluzbenec = %s
            AND datum >= CURRENT_TIMESTAMP
            ORDER BY datum ASC; 
    """, [id_usluzbenec])
    st_vrstic = cur.fetchone()
    return template('urnik_usluzbenca.html', id_usluzbenec=id_usluzbenec, urnik=cur, ime_priimek=ime_priimek, besedilo=besedilo,
                    st_vrstic=st_vrstic, ali_je_sef=ali_je_sef, besedilo2=besedilo2)


######################################################################################################
### POSLOVANJE

@get('/poslovanje')
@cookie_required_up_ime
@cookie_required_vloga
def poslovanje():
    up_ime = request.get_cookie('up_ime', secret=skrivnost)
    vloga = request.get_cookie('rola', secret=skrivnost)

    if vloga == 'usluzbenec':
      cur.execute("""select admin from Usluzbenec 
          where up_ime = %s""", [up_ime])
      ali_je_sef = cur.fetchone()[0]
    else:
        ali_je_sef = None

    cur.execute("""
        WITH a AS (
            SELECT t.id_termin, s.id_stranka, s.ime_priimek, t.datum, t.ime_storitve, t.ime_priimek_usluzbenca, st.trajanje, st.cena, i.popust,
                CASE WHEN i.popust IS NULL THEN cena
                  ELSE(1-i.popust) * st.cena 
                END AS koncna_cena, st.stroski, DATE_PART('month', datum) mesec, DATE_PART('year', datum) leto
            FROM Termin1 t
            LEFT JOIN Stranka s ON s.ime_priimek = t.ime_priimek_stranke
            LEFT JOIN Storitev st ON st.ime_storitve = t.ime_storitve
            LEFT JOIN Influencer i ON i.koda = t.koda
            WHERE t.datum <= CURRENT_TIMESTAMP
        ),
        b AS (
            SELECT DISTINCT leto, mesec, sum(koncna_cena) OVER(PARTITION BY leto, mesec) prihodki, 
            sum(stroski) OVER(PARTITION BY leto, mesec) odhodki
            FROM a
        )
        SELECT leto, mesec, prihodki, odhodki, prihodki - odhodki dobicek
        FROM b
        ORDER BY leto, mesec ASC;
    """)

    return template('poslovanje1.html', poslovanje=cur, ali_je_sef=ali_je_sef)


# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
#if __name__ == "__main__":
#    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

error(404)
def error_404(error):
    return "Ta stran ne obstaja!"

run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
