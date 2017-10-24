from bs4 import BeautifulSoup
import requests
import sqlalchemy
import csv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Scraping(Base):
    __tablename__ = 'scraping'
    insee_code = Column(String, primary_key=True)
    city = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    first_mandate_date = Column(String)
    scrap_web = Column(String)
    party = Column(String)

    def __repr__(self):
        return "<Mairies(insee_code='%s', city='%s', first_name='%s', last_name='%s', first_mandate_date='%s', party='%s')>" % (
            self.insee_code, self.city, self.first_name, self.last_name, self.first_mandate_date, self.party)


def raw_scraping(city, last_name, first_name):
	#try :
		r = requests.get("https://www.google.fr/search?q={}+{}+{}".format(city, last_name, first_name))
		soup = BeautifulSoup(r.text, "html.parser")

		head3 = soup.find_all("h3", class_="r", limit=5)
		urls = []
		raw = ""

		for title in head3[2:]:
			link = title.a['href']
			print(link)
			urls.append(link.split('&')[0][7:])

		for url in urls:
			r = requests.get(url)
			soup = BeautifulSoup(r.text, "html.parser")
			string = soup.body.get_text()
			raw += string
		raw = raw.replace(" ", "")
		raw = raw.replace("\n", "")
		return raw
	#except :
	#	return "NA"


def print_scraping(code, city, last_name, first_name):
	try :
		if int(code)<1040:
			return raw_scraping(city, last_name, first_name)
		else :
			return "NA"
	except :
		return "NA"


def build_db_scraping():
	outfile = open('static/insee.csv', 'r')
	reader = csv.DictReader(outfile, delimiter=';')
	for line in reader:
		print(line["codeinsee"])
		new_mayor = Scraping(
                insee_code=line["codeinsee"],
                city=line["libsubcom"],
                first_name=line["nompsn"],
                last_name=line["prepsn"],
                first_mandate_date="NA", 
                scrap_web=print_scraping(
                	line["codeinsee"],
                	line["libsubcom"],
                	line["prepsn"],
                	line["nompsn"]
                	),
                party="NA")
		session.merge(new_mayor)
		session.commit()
	outfile.close()


def write_csv(cvs_file):
	outfile = open(cvs_file, 'w')
	outcsv = csv.writer(outfile)
	outcsv.writerow(['insee_code', 'city', 'mayor_first_name', 'mayor_last_name', 'first_mandate_date', 'raw_scraping' 'party'])
	records = session.query(Scraping).all()
	session.commit()
	[outcsv.writerow([getattr(curr, column.name) for column in Scraping.__mapper__.columns]) for curr in records]
	outfile.close()


Base.metadata.create_all(engine)

print(raw_scraping('paris','anne','hidalgo'))

#build_db_scraping()
#write_csv('static/scraping_db.csv')
#print(raw_scraping('bonneville', 'saddier', 'martial'))