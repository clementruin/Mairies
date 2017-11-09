import sqlalchemy
import csv
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import mapper
import re
import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Mairies():
	pass

engine = create_engine('sqlite:///static/database_01.db', echo=False)
metadata = MetaData(engine)
mairies = Table('mairies', metadata, autoload=True)
mapper(Mairies, mairies)
# metadata.create_all() ??
Session = sessionmaker(bind=engine)
session = Session()

def no_accent(string):
    string = string.replace('é','e')
    string = string.replace('è','e')
    string = string.replace('ë','e')
    string = string.replace('ï','i')
    string = string.replace('É','e')
    string = string.replace('È','e')
    return string

def clean_party_attribute(string):
	string = no_accent(string)
	L = []
	se = ["SE", "sans etiquette", "Sans etiquette"]
	fn = ["FN","fn","National"]
	ump = ["UMP","Republicains","LR"]
	dvd = ["DVD","Divers Droite","divers droite", "Divers droite"]
	udi = ["UDI","Indep"]
	eelv = ["EELV","Ecologie","ecologie"]
	modem = ["MoDem","modem","MODEM"]
	dvg = ["DVG","Divers Gauche","divers gauche", "Divers gauche"]
	ps = ["PS","Socialiste","socialiste","ps"]
	fg = ["FG","fg","Front de Gauche","front de gauche", "Front de gauche"]
	pcf = ["PCF","Communiste","communiste"]
	prg = ["PRG","Radical"]
	#check parti radical ... 
	if any(i in string for i in se):
		L.append("SE")
	if any(i in string for i in fn):
		L.append("FN")
	if any(i in string for i in ump):
		L.append("UMP-LR")	
	if any(i in string for i in dvd):
		L.append("DVD")
	if any(i in string for i in udi):
		L.append("UDI")
	if any(i in string for i in eelv):
		L.append("EELV")
	if any(i in string for i in modem):
		L.append("MoDem")
	if any(i in string for i in dvg):
		L.append("DVG")
	if any(i in string for i in ps):
		L.append("PS")
	if any(i in string for i in fg):
		L.append("FG")
	if any(i in string for i in pcf):
		L.append("PCF")
	if any(i in string for i in prg):
		L.append("PRG")
	if len(L) == 0 :
		return "NA"
	else :
		return L[-1]


rows = session.query(Mairies).all()
for row in rows :
	row.party = clean_party_attribute(row.party)
	print(row.party)
session.commit() 


def write_csv():
    outfile = open('static/database_01.csv', 'w')
    outcsv = csv.writer(outfile)
    outcsv.writerow(['insee_code',
                     'postal_code',
                     'city',
                     'population'
                     'latitude',
                     'longitude',
                     'mayor_first_name',
                     'mayor_last_name',
                     'mayor_birthdate',
                     'first_mandate_date',
                     'party'])
    records = session.query(Mairies).all()
    session.commit()
    [outcsv.writerow([getattr(curr, column.name)
                      for column in mairies.c]) for curr in records]
    outfile.close()


write_csv()
#arbitrage, reecriture base 01!, puis Pandas .. 

