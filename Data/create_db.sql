-- Active: 1682070737195@@baza.fmf.uni-lj.si@5432@sem2023_klarat
CREATE TABLE Stranka (
    id_stranka SERIAL PRIMARY KEY,
    ime_priimek TEXT UNIQUE NOT NULL,
    telefon INTEGER UNIQUE NOT NULL,
    mail TEXT UNIQUE
);

CREATE TABLE Storitev (
    id_storitev SERIAL PRIMARY KEY,
    ime_storitve TEXT UNIQUE NOT NULL,
    trajanje integer not null,
    cena integer not null,
    stroski integer not null
);

CREATE TABLE Usluzbenec(
    id_usluzbenec serial,
    ime_priimek text unique not null,
    ime_storitve text references Storitev(ime_storitve),
    primary key (id_usluzbenec, ime_storitve)
   -- povprecna_ocena integer references Ocena()

);

create table Ocena(
    id_ocena serial primary key,
    ime_priimek text REFERENCES Usluzbenec(ime_priimek),
    ocena integer not null 
);

CREATE TABLE Influencer (
    id_kode serial primary key,
    koda text unique not null,
    ime_priimek text not null unique,
    popust decimal not null check (popust < 1)
);

create table Termin(
    id_termin SERIAL primary key,
    ime_priimek_stranke text not null REFERENCES Stranka(ime_priimek),
    datum date not null,
    ime_storitve text not null REFERENCES Storitev(ime_storitve),
    ime_priimek_usluzbenca text not null REFERENCES Usluzbenec(ime_priimek),
    koda text REFERENCES Influencer(koda)
);


GRANT CONNECT ON DATABASE sem2023_klarat TO javnost;
GRANT USAGE ON SCHEMA public TO javnost;
GRANT ALL ON DATABASE sem2023_klarat TO sarac WITH GRANT OPTION;
GRANT ALL ON ALL TABLES IN SCHEMA public TO sarac WITH GRANT OPTION;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO sarac WITH GRANT OPTION;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;

-- dodatne pravice za uporabo aplikacije

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO javnost;

GRANT ALL ON DATABASE sem2023_klarat TO majak WITH GRANT OPTION;
GRANT ALL ON ALL TABLES IN SCHEMA public TO majak WITH GRANT OPTION;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO majak WITH GRANT OPTION;



