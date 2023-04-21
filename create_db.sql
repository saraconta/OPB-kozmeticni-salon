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
    id_storitev integer references Storitev(id_storitev),
    primary key (id_usluzbenec, id_storitev)
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

insert into Influencer(koda, ime_priimek, popust) values('SPELA10', 'Špela Novak', 0.10);
insert into Influencer(koda, ime_priimek, popust) values('ANA30', 'Ana Kovač', 0.30);
insert into Influencer(koda, ime_priimek, popust) values('KATARINA15', 'Katarina Kos', 0.15);
insert into Influencer(koda, ime_priimek, popust) values('MARIJA20', 'Marija Vodopivec', 0.20);
insert into Influencer(koda, ime_priimek, popust) values('TIA40', 'Tia Klobasa', 0.40);
insert into Influencer(koda, ime_priimek, popust) values('EMA10', 'Ema Oblak', 0.10);
insert into Influencer(koda, ime_priimek, popust) values('HANA20', 'Hana Režek', 0.20);

insert into Influencer(koda, ime_priimek, popust) values('IZA15', 'Iza Torek', 0.15);

insert into Influencer(koda, ime_priimek, popust) values('PAULINA30', 'Paulina Cankar', 0.30);

insert into Influencer(koda, ime_priimek, popust) values('REBEKA30', 'Rebeka Korenjak', 0.30);


insert into Storitev(ime_storitve, trajanje, cena, stroski) values('žensko striženje', 30,35,10 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('moško striženje', 20,25,5 );

insert into Storitev(ime_storitve, trajanje, cena, stroski) values('pedikura', 30,35,5 );

insert into Storitev(ime_storitve, trajanje, cena, stroski) values('manikura', 45,40,20 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('barvanje', 60,70,30 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('depilacija nog', 15,40,10 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('depilacija bikini predela', 10,20,5 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('depilacija pazduh', 5,15,5 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('depilacija celega telesa', 45,50,10 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('ličenje', 45,50,20 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('fen frizura', 30,35,10 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('masaža', 50,35,5 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('laminacija obrvi', 30,35,5 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('podaljševanje trepalnic', 45,50,20 );

insert into Storitev(ime_storitve, trajanje, cena, stroski) values('medicinska pedikura', 20,40,10 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('lasersko odstranjevanje dlak', 60,80,20 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('urejanje brade', 20,30,10 );
insert into Storitev(ime_storitve, trajanje, cena, stroski) values('nega las in lasišča', 25,20,5 );




