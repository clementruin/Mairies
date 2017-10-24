import sqlalchemy
import csv
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
import re
import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

engine = create_engine('sqlite:///static/database.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class TableError(Exception):
    pass

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


dict = {}
outfile = open('static/code_postaux_insee.csv', 'r')
reader = csv.DictReader(outfile, delimiter=';')
for line in reader:
    dict[line["Code_commune_INSEE"]] = [
        line["Code_postal"], line["coordonnees_gps"]]


def get_dict(code):
    # associates insee_code with postal_code and coordinates
    try:
        return (dict[code][0],
                dict[code][1].split(',')[0],
                dict[code][1].split(', ')[1])
    except BaseException:
        return ("None", "None", "None")


def no_accent(string):
    string = string.replace('é','e')
    string = string.replace('è','e')
    string = string.replace('ë','e')
    string = string.replace('ï','i')
    string = string.replace('É','e')
    string = string.replace('È','e')
    return string


def build_db():
    outfile = open('static/insee.csv', 'r')
    reader = csv.DictReader(outfile, delimiter=';')
    for line in reader:
        get = get_dict(line["codeinsee"])
        scrap = scrap_party_date(
            get[0],
            line["libsubcom"],
            line["prepsn"],
            line["nompsn"])
        print(line["codeinsee"])
        #print(scrap)
        new_mayor = Mairies(
            insee_code=line["codeinsee"],
            postal_code=get[0],
            city=line["libsubcom"],
            latitude=get[1],
            longitude=get[2],
            first_name=line["nompsn"],
            last_name=line["prepsn"],
            birthdate=line["naissance"],
            first_mandate_date=scrap[0],
            party=scrap[1])
        session.merge(new_mayor)
    session.commit()
    outfile.close()


def write_csv():
    outfile = open('static/database.csv', 'w')
    outcsv = csv.writer(outfile)
    outcsv.writerow(['insee_code',
                     'postal_code',
                     'city',
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
                      for column in Mairies.__mapper__.columns]) for curr in records]
    outfile.close()


def scrap_party_date(postal_code, city, first_name, last_name):
    try:
        city = unidecode.unidecode(city)
        url = "https://www.google.fr/search?q={}+{}+{}".format(
            'wikipedia', city, postal_code)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        #head3 = soup.find_all("h3", class_="r", limit=1)
        #link = head3[0].a['href']
        #link = link.split('=')[1].split('&')[0]
        #pattern = re.compile(r'Liste des maires successifs')
        #caption = soup.find('caption', text=pattern).parent
        #table = caption.parent

        tag = soup.find_all("div", class_="kv", limit=1)
        link = tag[0].cite.text

        r = requests.get(link)
        soup = BeautifulSoup(r.text, "lxml")
        mayor_table = soup.find_all(
            "table", class_="wikitable centre communes")
        data = []
        for tables in mayor_table:
            for row in tables.find_all("tr"):
                L = row.find_all("td")
                if len(L) > 2:
                    data.append([ele.text for ele in L])

        min_date = 4000
        min_index = None
        for i in range(len(data)):
            if fuzz.token_sort_ratio(no_accent(data[i][2]), no_accent(first_name +" "+last_name)) > 80:
                curr_date = re.search(r"(\d{4})", data[i][0]).group(1)
                if int(curr_date) < min_date:
                    min_date = int(curr_date)
                    min_index = i
        if min_index == None:
            raise TableError()
        else :    
            return (re.search(r"(\d{4})", data[min_index][0]).group(1), data[min_index][3])
    except TableError:
        print("Impossible Match in WikiTable")
        return ("Error found", "Error found")
    except BaseException:
        return("Error found", "Error found")


Base.metadata.create_all(engine)

#print(scrap_party_date('01182','Groslée','Marthe','AUREL'))
build_db()
write_csv()