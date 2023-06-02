#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *
import sqlite3

# uvozimo ustrezne podatke za povezavo

from Data.model import *
from Database import Repo

# from Data.services import AuthService
from functools import wraps

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


#auth = AuthService(repo)

#def cookie_required(f):
#    """
#    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
#    """
#    @wraps(f)
#    def decorated( *args, **kwargs):
#
#
#        cookie = request.get_cookie("uporabnik")
#        if cookie:
#            return f(*args, **kwargs)
#
#        return template("prijava.html", napaka="Potrebna je prijava!")
#
#
#
#
#    return decorated
#  
#@get('/odjava')
#def odjava():
#    """
#    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
#    """
#    
#    response.delete_cookie("uporabnik")
#    response.delete_cookie("rola")
#    
#    return template('zacetna_stran.html', napaka=None)
#  
#@get('/usluzbenec/prijava') 
#def prijava_usluzbenec_get():
#    return template("usluzbenec_prijava.html")
#
##manjka post za prijavo usluzbenca
# @post('/usluzbenec/prijava') 
# def prijava_usluzbenec_post():
#     uporabnisko_ime = request.forms.get('uporabnisko_ime')
#     geslo = request.forms.get('geslo')
#     if uporabnisko_ime is None or geslo is None:
#         redirect(url('prijava_usluzbenec_get'))
#     hashBaza = None
#     try: 
#         cur.execute("SELECT geslo FROM usluzbenec WHERE uporabnisko_ime = %s", [uporabnisko_ime])
#         hashBaza = cur.fetchall()[0][0]
#     except:
#         hashBaza = None
#     if hashBaza is None:
#         redirect(url('prijava_usluzbenec_get'))
#         return
#     if geslo != hashBaza:
#       #  nastaviSporocilo('Nekaj je šlo narobe.') 
#         redirect(url('prijava_usluzbenec_get'))
#         return
#     response.set_cookie("uporabnisko_ime", uporabnisko_ime,  path = "/") #secret = "secret_value",, httponly = True)
#     response.set_cookie("rola", "usluzbenec",  path = "/")
  
#@get('/stranka/prijava') 
#def prijava_stranka_get():
#    return template("stranka_prijava.html")
#  
#manjka post za prijavo stranke
# @post('/stranka/prijava') 
# def prijava_stranka_post():
#     uporabnisko_ime = request.forms.get('uporabnisko_ime')
#     geslo = request.forms.get('geslo')
#     if uporabnisko_ime is None or geslo is None:
#         redirect(url('prijava_usluzbenec_get'))
#     hashBaza = None
#     try: 
#         cur.execute("SELECT geslo FROM stranka WHERE uporabnisko_ime = %s", [uporabnisko_ime])
#         hashBaza = cur.fetchall()[0][0]
#     except:
#         hashBaza = None
#     if hashBaza is None:
#         redirect(url('prijava_stranka_get'))
#         return
#     if geslo != hashBaza:
#       #  nastaviSporocilo('Nekaj je šlo narobe.') 
#         redirect(url('prijava_stranka_get'))
#         return
#     response.set_cookie("uporabnisko_ime", uporabnisko_ime,  path = "/") #secret = "secret_value",, httponly = True)
#     response.set_cookie("rola", "stranka",  path = "/")


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
  try:
      cur.execute("""
      INSERT INTO Stranka (ime_priimek, telefon, mail)
      VALUES (%s, %s, %s) RETURNING id_stranka; 
    """, (ime_priimek, telefon, mail)
    )
      conn.commit()
  except Exception as ex:
      conn.rollback()
      return template('dodaj_stranko.html', ime_priimek=ime_priimek, telefon=telefon,mail = mail,
                    napaka='Zgodila se je napaka: (%s, %s, %s)' % ex)
  redirect(url('/'))

@get('/prijava_stranka')
#@cookie_required
def prijava_stranka():
    return template('prijava_stranka.html', uporabnisko_ime='', geslo='', napake=None)

#manjka post poizvedba, pride ko bodo urejene prijave
  

### USLUŽBENCI
@get('/usluzbenci')
def usluzbenci():
    cur.execute("""
        WITH povpr AS (SELECT ime_priimek, round(avg(ocena),2) povprecna_ocena
          FROM Ocena
          GROUP BY ime_priimek) 
        SELECT u.*, p.povprecna_ocena
        FROM usluzbenec u
        LEFT JOIN povpr p ON p.ime_priimek = u.ime_priimek
        order by u.ime_priimek asc;
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
  try:
      cur.execute("""
          with ins1 as(
          INSERT INTO Usluzbenec (ime_priimek) VALUES (%s) RETURNING id_usluzbenec
          )
          INSERT INTO Usluzb_storitve (id_usluzbenec, ime_storitve)
          SELECT id_usluzbenec, %s FROM ins1;

        """, (ime_priimek, storitev)
        )
      conn.commit()
  except Exception as ex:
      conn.rollback()
      return template('dodaj_usluzbenca.html', ime_priimek=ime_priimek, storitev=storitev,
                    napaka='Zgodila se je napaka: %s' % ex)
  redirect(url('/uluzbenci'))

@get('/prijava_usluzbenec')
#@cookie_required
def prijava_usluzbenec():
    return template('prijava_usluzbenec.html', uporabnisko_ime='', geslo='', napake=None)

#manjka post poizvedba, pride ko bodo urejene prijave


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
    redirect(url('/usluzbenci'))

@get('/storitve/<id_usluzbenec:int>')
def storitve(id_usluzbenec):
    cur.execute("""SELECT us.ime_storitve ime1, 1 ime2
                  FROM Usluzb_storitve us
                  WHERE us.id_usluzbenec = %s""", [id_usluzbenec])
    return template('storitve.html', id_usluzbenec = id_usluzbenec, storitve=cur, napaka=None)


### STORITVE
@get('/dodaj_storitev/<id_usluzbenec:int>')
#@cookie_required
def dodaj_storitev(id_usluzbenec): 
    cur.execute("""SELECT  
                    u.ime_priimek
                    FROM Usluzbenec u
                    WHERE u.id_usluzbenec = %s;""",
                    [id_usluzbenec])




    

    return template('dodaj_storitev.html', id_usluzbenec = id_usluzbenec,
                    ime_priimek=cur.fetchone()[0], storitev='',
                    napaka=None)


@post('/dodaj_storitev/<id_usluzbenec:int>')
def dodaj_storitev_post(id_usluzbenec):
  storitev = request.forms.storitev
  #storitev = request.forms.get('storitev')
  cur.execute("""

        INSERT INTO Usluzb_storitve (id_usluzbenec, ime_storitve) VALUES (%s, %s);

        """, (id_usluzbenec, storitev)
  )
  conn.commit()
  redirect(url('/usluzbenci'))




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
def termin_stranka(id_usluzbenec, id_storitev):
    cur.execute("""
      SELECT u.ime_priimek, s.ime_storitve, s.trajanje, u.id_usluzbenec, s.id_storitev
      FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
      WHERE (u.id_usluzbenec, s.id_storitev) = (%s, %s);""", (id_usluzbenec, id_storitev))
    vrstica=cur.fetchone()
    return template('termin.html', id_storitev = id_storitev, id_usluzbenec = id_usluzbenec, 
      ime_priimek_usluzbenca=vrstica[0], ime_storitve=vrstica[1],
      datum='', 
      napaka=None)
#, , ime_priimek_stranke='', koda='', napaka=None)

@get('/termin/<id_storitev:int>/<id_usluzbenec:int>/')
def termin_date_conversion(id_usluzbenec, id_storitev):
    datum = request.query.datum # dobimo datum iz urlja
    year = datum[0:4]
    month = datum[5:7]
    day = datum[8:10]
    
    # redirect na termin_ura s pravilno oblikovanim datumom
    return redirect(url('termin_ura', id_usluzbenec=id_usluzbenec, id_storitev=id_storitev, year=year, month=month, day=day))


@get('/termin/<id_storitev:int>/<id_usluzbenec:int>/<year:int>-<month:int>-<day:int>')
#@cookie_required
def termin_ura(id_usluzbenec, id_storitev, year, month, day):
    datum = f"{year}-{month}-{day}"  # nastavimo parameter datum
    cur.execute("""with a as (select 
      t.datum::time zacetek,   t.datum::time + (s.trajanje * interval '1 Minute' ) konec
      from termin1 t
      left join usluzbenec u on t.ime_priimek_usluzbenca = u.ime_priimek
      left join storitev s on t.ime_storitve = s.ime_storitve
      where id_usluzbenec  = %s
      and t.datum::date = %s)
      select ur.zacetek, a.konec
      from Ure ur
      left join a on a.zacetek = ur.zacetek
      where a.zacetek is null;""", [id_usluzbenec, datum])
    #prosti_termini = cur.fetchall()
    #cur.execute("""
    #  select 
    #  t.datum::time zacetek,  t.datum::time + (s.trajanje * interval '1 Minute' ) konec
    #  from termin1 t
    #  left join usluzbenec u on t.ime_priimek_usluzbenca = u.ime_priimek
    #  left join storitev s on t.ime_storitve = s.ime_storitve
    #  where id_usluzbenec  = %s
    #  and t.datum::date = %s""", [id_usluzbenec, datum] )
    #zasedene_ure = cur.fetchall()
    #mozni_termini = []
    #for i in range(8, 16):
    #    mozni_termini.append((f"{i}::00", f"{i+1}::00", False))
#
    #prosti_termini = []
    #for z, k, zs in mozni_termini:
    #    for z1 in zasedene_ure:
    #        if z1 == datetime.strptime(z, '%H::%M').time():
    #            zs = True
    #        if zs == False:
    #            prosti_termini.append(z)


    return template('termin_ura.html', id_storitev = id_storitev, id_usluzbenec = id_usluzbenec,
                    datum = datum,year=year, month=month, day=day, 
      ura = cur, ime_priimek_stranke = '', koda = '', napaka=None)




@post('/termin/<id_storitev:int>/<id_usluzbenec:int>/<year:int>-<month:int>-<day:int>')
def vpis_termina_post(id_usluzbenec, id_storitev, year, month, day):
    datum = f"{year}-{month}-{day}"
    cur.execute("""
      SELECT u.ime_priimek, s.ime_storitve, s.trajanje, u.id_usluzbenec, s.id_storitev
      FROM Storitev s
      LEFT JOIN Usluzb_storitve us ON us.ime_storitve = s.ime_storitve
      LEFT JOIN Usluzbenec u ON u.id_usluzbenec = us.id_usluzbenec
      WHERE (u.id_usluzbenec, s.id_storitev) = (%s, %s)""", (id_usluzbenec, id_storitev))
    
    vrstica=cur.fetchone()
    ime_priimek_stranke = request.forms.ime_priimek_stranke
    ura = request.forms.ura
    datum_ura = datum + " " + ura
    ime_storitve = vrstica[1]
    ime_priimek_usluzbenca = vrstica[0]
    koda = request.forms.koda
    
    cur.execute("""
      INSERT INTO Termin1 (ime_priimek_stranke, datum, ime_storitve, ime_priimek_usluzbenca, koda)
      VALUES (%s, %s, %s, %s, %s) RETURNING id_termin;
      """, (ime_priimek_stranke, datum_ura, ime_storitve, ime_priimek_usluzbenca, koda)
      )
    conn.commit()

    #redirect(url('/prikazi_termin/<id_termin:int>')) #kako bi pridobili ta id_termin?? 
    redirect(url('/'))

#sem spremenila select, zdaj bi moglo pravilno use pokazat in izračunat končno ceno, samo za ta
#id_stranka neki teži, najbrž ker v zgornjem post ne zna pridobiti id_stranka
@get('/prikazi_termin/<id_termin:int>')
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
      WHERE t.id_termin = %s;""", [id_termin])

    return template('termin_prikazi.html', id_termin=id_termin, termin=cur)



@get('/pregled_terminov')
def pregled_terminov():
    cur.execute("""
      SELECT id_stranka, ime_priimek from Stranka 
      order by ime_priimek
    """)
    return bottle.template('pregled_terminov.html', stranke=cur)


@get('/pregled_termina/<id_stranka:int>')
#@cookie_required
def pregled_termina(id_stranka): 
    cur.execute("""SELECT id_termin, datum, ime_storitve
                    FROM termin1
                    LEFT JOIN stranka
                    ON termin1.ime_priimek_stranke = stranka.ime_priimek
                    WHERE id_stranka = %s
                    ;""",
                    [id_stranka])
    return template('pregled_termina.html',
                    tabela=cur,
                    napaka=None)

@post('/izbrisi_termin')
def pobrisi_termin():
    id_termin = request.forms.id_termin
    cur.execute("""DELETE FROM termin1 WHERE id_termin = %s""", [id_termin])
    conn.commit()
    redirect(url('/pregled_terminov'))



### URNIK
@get('/urnik')
def urnik():
    cur.execute("""
      SELECT u.* FROM usluzbenec u
      ORDER BY ime_priimek;
      """)
    return bottle.template('urnik.html', usluzbenci=cur)

@get('/urnik/<id_usluzbenec:int>')
def prikazi_urnik(id_usluzbenec):
    cur.execute("""
        SELECT ime_priimek_stranke, datum, ime_storitve
        FROM Termin1 t
        JOIN Usluzbenec u ON u.ime_priimek = t.ime_priimek_usluzbenca 
        WHERE id_usluzbenec = %s
        AND datum >= CURRENT_TIMESTAMP
        ORDER BY datum ASC; """, [id_usluzbenec])
    
    return template('urnik_usluzbenca.html', id_usluzbenec=id_usluzbenec, urnik=cur)

#POSLOVANJE
@get('/poslovanje')
def poslovanje():
    cur.execute("""
        with a as 
          (SELECT t.id_termin, s.id_stranka, s.ime_priimek, t.datum, t.ime_storitve, t.ime_priimek_usluzbenca, st.trajanje, st.cena, i.popust,
              CASE WHEN i.popust IS NULL THEN cena
                  ELSE(1-i.popust) * st.cena 
              END AS koncna_cena, st.stroski, DATE_PART('month', datum) mesec, DATE_PART('year', datum) leto
          FROM Termin1 t
          LEFT JOIN Stranka s ON s.ime_priimek = t.ime_priimek_stranke
          LEFT JOIN Storitev st ON st.ime_storitve = t.ime_storitve
          LEFT JOIN Influencer i ON i.koda = t.koda),
        b as 
          (SELECT DISTINCT leto, mesec, sum(koncna_cena) OVER(PARTITION BY leto, mesec) prihodki, 
          sum(stroski) OVER(PARTITION BY leto, mesec) odhodki
          FROM a)
        SELECT leto, mesec, prihodki, odhodki, prihodki - odhodki dobicek
        FROM b
        ORDER BY leto, mesec ASC;
    """)
    return bottle.template('poslovanje.html', poslovanje=cur)



# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
#if __name__ == "__main__":
#    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

@bottle.error(404)
def error_404(error):
    return "Ta stran ne obstaja!"

bottle.run(reload=True, debug=True)