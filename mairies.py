import sqlalchemy
import csv
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
#import scraping 

engine = create_engine('sqlite:///database.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Mairies(Base):
    __tablename__ = 'mairies'
    insee_code = Column(String, primary_key=True)
    postal_code = Column(Integer)
    city = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(String)
    first_mandate_date = Column(String)
    party = Column(String)

    def __repr__(self):
        return "<Mairies(insee_code='%s', postal_code='%s', city='%s', latitude='%s', longitude='%s', first_name='%s', last_name='%s', birthdate='%s', first_mandate_date='%s', party='%s')>" % (
            self.insee_code, self.postal_code, self.city, self.latitude, self.longitude, self.first_name, self.last_name, self.birthdate, self.first_mandate_date, self.party)


dict={}
outfile = open('static/code_postaux_insee.csv', 'r')
reader = csv.DictReader(outfile, delimiter=';')
for line in reader:
	dict[line["Code_commune_INSEE"]] = [line["Code_postal"],line["coordonnees_gps"]]


def get_dict(code):
	try :
		return (dict[code][0],
				dict[code][1].split(',')[0],
				dict[code][1].split(', ')[1])
	except :
		return ("None", "None", "None")


def build_db():
	outfile = open('static/insee.csv', 'r')
	reader = csv.DictReader(outfile, delimiter=';')
	for line in reader:
		get = get_dict(line["codeinsee"])
		new_mayor = Mairies(
                insee_code=line["codeinsee"],
                postal_code=get[0],
                city=line["libsubcom"],
                latitude=get[1],
                longitude=get[2],
                first_name=line["nompsn"],
                last_name=line["prepsn"],
                birthdate=line["naissance"],
                first_mandate_date="None", 
                party=scrap_party(line["codeinsee"],line["libsubcom"]))
		session.merge(new_mayor)
		session.commit()
	outfile.close()

def write_csv():
	outfile = open('static/dpt01_db.csv', 'w')
	outcsv = csv.writer(outfile)
	outcsv.writerow(['insee_code', 'postal_code', 'city', 'latitude', 'longitude', 'mayor_first_name', 'mayor_last_name', 'mayor_birthdate', 'first_mandate_date', 'party'])
	records = session.query(Mairies).all()
	session.commit()
	[outcsv.writerow([getattr(curr, column.name) for column in Mairies.__mapper__.columns]) for curr in records]
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

		print(insee_code, party)
		return party
	except :
		print(insee_code, "Not Available")
		return "Not Available"

Base.metadata.create_all(engine)

build_db()
write_csv()