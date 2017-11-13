import pandas as pd
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
import matplotlib.pyplot as plt
import numpy as np
import math

class Mairies():
	pass

engine = create_engine('sqlite:///static/database.db', echo=False)
metadata = MetaData(engine)
mairies = Table('mairies', metadata, autoload=True)
mapper(Mairies, mairies)
Session = sessionmaker(bind=engine)
session = Session()

def data_frame(query, columns):
    """
    Takes a sqlalchemy query and a list of columns, returns a dataframe.
    """
    def make_row(x):
        return dict([(c, getattr(x, c)) for c in columns])       
    return pd.DataFrame([make_row(x) for x in query])

# dataframe with all fields in the table
query = session.query(Mairies).all()
df = data_frame(query, ["insee_code","postal_code","city", "population" ,"latitude" ,"longitude","first_name","last_name","birthdate","first_mandate_date","party"])
df["population"] = df["population"].apply(pd.to_numeric)


def city_map():
	Y = df.as_matrix(columns=df.columns[6:8])[:,0]
	X = df.as_matrix(columns=df.columns[6:8])[:,1]

	A = []
	for y in Y:
		if y == "None":
			A.append(-np.cos(48.8*np.pi/180))
		else :
			y = float(y)
			y = np.cos(y*np.pi/180)
			A.append(-y)

	B = []
	for x in X:
		if x == "None":
			B.append(np.sin(2.02*np.pi/180))
		else :
			x = float(x)
			x = np.sin(x*np.pi/180)
			B.append(x)


	plt.plot(B,A, ".")
	plt.show()


def pop_per_party(range):
	# population under each party
	pop = df.loc[:,['population','party','city']]
	pop = pop[pop.population >= range[0]][pop.population <= range[1]].groupby("party").sum().sort_values("population")
	total_pop = pop['population'].sum()
	pop["percentage"] = pop["population"].apply(lambda x: x/total_pop*100)
	print(pop)

def party_vs_citysize(df):
	Sizes = [0,200, 600, 1000, 5000, 10000, 30000, 70000, 100000, 300000, 1000000]
	Parties = ["UMP-LR","PS", "DVD", "DVG", "SE"]
	n = len(Sizes)
	A = []
	df_pop = df.loc[:,['population','party']]
	for s in Sizes:
		L = []
		total_pop = df_pop['population'][df_pop.population >= s].sum()
		for p in Parties:
			n_pop = df_pop[df_pop.population >= s][df_pop.party==p]
			n_pop = n_pop['population'].sum()/total_pop*100
			L.append(n_pop)
		A.append(L)
	df = pd.DataFrame(A, index=Sizes, columns=Parties)
	df.plot.bar()
	plt.show()


#----- main -----#
population_threshold = [0,1000000]
#city_map()
pop_per_party(population_threshold)
#party_vs_citysize(df)
