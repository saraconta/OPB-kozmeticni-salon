from dataclasses import dataclass, field

@dataclass
class Stranka:
    id_stranka: int = field(default=0)
    ime_priimek: str = field(default="")
    telefon: int = field(default=0)
    mail: str = field(default="")

@dataclass
class Storitev:
    id_storitev: int = field(default=0)
    ime_storitve: str = field(default="")
    trajanje: int = field(default=0)
    cena: int = field(default=0)
    stroski: int = field(default=0)

@dataclass
class Usluzbenec:
    id_usluzbenec: int = field(default=0)
    ime_priimek: str = field(default="")
    id_storitve: int = field(default=0)

@dataclass
class Ocena:
    id_ocena: int = field(default=0)
    ime_priimek: str = field(default="")
    ocena: int = field(default=0)

@dataclass
class Influencer:
    id_kode: int = field(default=0)
    koda: str = field(default="")
    ime_priimek: str = field(default="")
    popust: float = field(default=0)

@dataclass
class Termin:
    id_termina: int = field(default=0)
    ime_priimek_stranke: str = field(default="")
    datum: str = field(default="")
    ime_storitve: str = field(default="")
    ime_priimek_usluzbenca: str = field(default="")
    koda: str = field(default="")





