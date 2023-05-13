from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
from typing import Dict
from re import sub
import dataclasses


# Vse kar delamo z bazo se nahaja v razredu Repo.
repo = Repo()
auth = AuthService(repo)



@@ -106,6 +108,13 @@ def uvozi_csv(pot, ime):

# uvozi_csv(pot, "NovaTabela")

# primer ročnega dodajanja uporabnikov

uporabnik1 = auth.dodaj_uporabnika("gasper", "user", "gasper")

uporabnik = auth.dodaj_uporabnika("admin", "admin", "admin")


