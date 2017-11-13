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

engine = create_engine('sqlite:///static/database.db', echo=False)
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


def write_csv():
    outfile = open('static/database.csv', 'w')
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

def scrap_party(insee_code, city):
	try :
		r = requests.get("https://www.google.fr/search?q={}+{}+{}+{}".format('le', 'monde', city, insee_code))
		soup = BeautifulSoup(r.text, "html.parser")
		head3 = soup.find_all("h3", class_="r", limit=1)
		link = head3[0].a['href']
		link = link.split('=')[1].split('&')[0]
		link = link.split(insee_code)[0]+insee_code

		r = requests.get(link)
		soup = BeautifulSoup(r.text, "lxml")
		div = soup.find_all("div", class_="elu-principal")
		party = div[0].ul.li.br.next_sibling
		return party
	except :
		return "NA"

"""
## correction pour les communes sans parti
rows = session.query(Mairies).filter(Mairies.party == "NA").filter(Mairies.population<5000).filter(Mairies.population>2500).all()
for row in rows :
	#row.party = clean_party_attribute(scrap_party(row.insee_code, row.city))
	print(row.city, row.party, row.population)
print(len(rows))
session.commit() 
"""

"""
row = session.query(Mairies).filter(Mairies.city=="Paris").all()
row[0].party = "PS"
row[0].first_mandate_date = "2014"
session.commit()
"""

"""
## Nettoie les parties après avoir génerer la base brute avec mairies.py
rows = session.query(Mairies).all()
for row in rows :
	row.party = clean_party_attribute(row.party)
	print(row.party)
session.commit() 
"""

write_csv()

