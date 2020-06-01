# ######################################################
# This code is to get Covid-19 data from Brasil.io
# And then merge it with IDH info
# ######################################################

import requests
import pandas as pd
import json
from datetime import date
import numpy as np
import os
import csv
import inspect

# Setting the variables
api_get = "https://brasil.io/api/dataset/covid19/caso_full/data"
results = []
notes = []
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Getting the data
while api_get != None:
    response = requests.get(api_get)
    data = response.json()
    results.extend(data["results"])
    api_get = data["next"]
    count = data["count"]
response.close()
# results[-1]

# Putting info into a Panda Dataframe and doing some checks
covid_munic = pd.DataFrame(results)
covid_munic["date"] = pd.to_datetime(covid_munic['date'], format="%Y/%m/%d")

# Is our counts right?
if len(results) == count == len(covid_munic):
    notes.append("All data from Brasil.IO with same count")
else:
    notes.append("We got some number wrong (Number of cases Brasil.io)")
    notes.append("API: {}".format(len(results)))
    notes.append("API count: {}".format(count))
    notes.append("Our database: {}".format(len(covid_munic)))

# Checking the data for Brasil.io
#Last dates
notes.append("\n\nLast dates on date and by city")
notes.append(covid_munic[["date", "last_available_date"]].max())
#Any changes on columns names
columns_before = ['city', 'city_ibge_code', 'date', 'epidemiological_week',
      'estimated_population_2019', 'is_last', 'is_repeated',
      'last_available_confirmed',
      'last_available_confirmed_per_100k_inhabitants', 'last_available_date',
      'last_available_death_rate', 'last_available_deaths', 'new_confirmed',
      'new_deaths', 'order_for_place', 'place_type', 'state']
columns_now = covid_munic.columns.to_list()
missing_col = added_col = []
for i in columns_before:
    if i not in columns_now:
        missing_col.append(i)
for i in columns_now:
    if i not in columns_before:
        added_col.append()
notes.append("\n\Columns added or excluded?")
if len(added_col) > 0 | len(missing_col)>0:
    notes.append("Columns missing: {}".format(missing_col))
    notes.append("Columns added: {}".format(added_col))
else:
    notes.append("No")
#Total numbers
notes.append("\n\nTotals for confirmed and death")
notes.append(covid_munic.groupby("place_type").agg({"new_confirmed":'sum', "new_deaths": 'sum', "estimated_population_2019": 'sum'}))
#Last 10 days
notes.append("\n\nNumber of UF on last 10 days with a case or death")
notes.append(covid_munic[(covid_munic["new_confirmed"] > 0) | (covid_munic["new_deaths"] > 0)].groupby("date")["state"].nunique().tail(10))



# Adding indicators
indicators = pd.read_excel("data\IndicadoresSociais_mun.xlsx")
merged = pd.merge(covid_munic, indicators, how='left', left_on='city_ibge_code', right_on='codigo_ibge',
         copy=True, indicator=False, validate=None)

# Fix some city names
merged.loc[merged["city_ibge_code"] == 1708254, ['city']] = "Fortaleza do Tabocão"
merged.loc[merged["city_ibge_code"] == 2802601,["city"]] = "Gracho Cardoso"
merged.loc[merged["city_ibge_code"] == 2405306,["nome"]] = "Januário Cicco"
merged.loc[merged["city_ibge_code"] == 2512606,["nome"]] = "Quixaba"
merged.loc[merged["city_ibge_code"] == 2613107,["nome"]] = "São Caitano"
merged.loc[merged["city_ibge_code"] == 2918803,["nome"]] = "Laje"
merged.loc[merged["city_ibge_code"] == 2918902,["nome"]] = "Lajedão"
merged.loc[merged["city_ibge_code"] == 2919058,["nome"]] = "Lajedo do Tabocal"
merged.loc[merged["city_ibge_code"] == 4215695,["nome"]] = "Santiago do Sul"


# Checks on indicators
# Any cities have different names (We are missing states names in Brasil.io, so using from indicators)
notes.append("\n\nCity names different from Brasil.io and Indicadores")
notes.append(merged[(merged["city"] != merged["nome"]) & (merged["place_type"] == "city")
    & (merged["city"] != "Importados/Indefinidos")][["city_ibge_code","codigo_ibge","city",
    "nome"]].groupby(["city_ibge_code","codigo_ibge","city", "nome"]).count())
#Missing any info from Indicators
notes.append("\n\nMissing any info in Indicadores?")
notes.append(merged[(merged['nome'].isnull()) & (merged['city'] != 'Importados/Indefinidos')].groupby(["place_type", "city"])["state"].count())



# Clean the merged file and put it into a file
merged.drop(["codigo_ibge", "tipo", "UF", "nome.1", "latitude.1", "longitude.1", "tipo.1", "Região.1", "codigo_uf.1"], axis = 1, inplace = True)
merged.rename(columns={"nome": "name", "Região":"Region", "codigo_uf": "code_state"}, inplace=True)
merged.to_csv("data\caso_full_with_indicators.csv", index=False)


# Now let's put the notes into a file
notes.append("\n\nFinal Columns")
notes.append(merged.columns)

with open('data\load_brasilio_notes.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for row in zip(notes):
        writer.writerow(row)

