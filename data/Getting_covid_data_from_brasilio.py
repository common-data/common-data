# ######################################################
# This code is to get Covid-19 data from Brasil.io
# And then merge it with IDH info
# ######################################################

import requests
import pandas as pd
import json
from datetime import date, timedelta, datetime
import time
import numpy as np
import os
import csv
import inspect

# Setting the variables
notes = []
results = []
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

date_list = pd.to_datetime(pd.date_range(date.today() - timedelta(1), periods=12, freq='-1D').tolist(), format='%Y%m%d')

# Getting our current data
covid_munic_exc = pd.read_csv("data\caso_full_with_indicators.csv")
covid_munic_exc["date"] = pd.to_datetime(covid_munic_exc['date'], format="%Y/%m/%d")
covid_munic_exc = covid_munic_exc[covid_munic_exc["date"] < min(date_list)]

count = 0
# Getting the data
for date in date_list:
    cleaning = 1
    api_get = "https://brasil.io/api/dataset/covid19/caso_full/data/?date="
    print(datetime.now(), ": ", date)
    while api_get != None:
        if cleaning == 1:
            date_api = date.strftime("%Y-%m-%d")
        else:
            date_api = ""
        response = requests.get(api_get + date_api)
        data = response.json()
        results.extend(data["results"])
        api_get = data["next"]
        cleaning = 0

    # time.sleep(45)
    count += data["count"]
response.close()
# results[-1]

results = pd.DataFrame(results)
results["date"] = pd.to_datetime(results['date'], format="%Y/%m/%d")
# Let's put both datas together now
covid_munic = pd.concat([covid_munic_exc, results.sort_values(["date", "city_ibge_code"])])

# Is our counts right?
if len(results) == count:
    notes.append("All data from Brasil.IO with same count: {}".format(count))
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
        added_col.append(i)
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


# ###### Cleaning caso_full
covid_munic.sort_values(["city_ibge_code", "state", "date"], inplace=True)
covid_munic["city_ibge_code"] = covid_munic["city_ibge_code"].fillna(9)

# Cities that had positive on first day and then negative on next update, let's transform both to zero
clean_df = covid_munic[(covid_munic["new_confirmed"] != 0) | (covid_munic["new_deaths"] != 0)]
# clean_df[clean_df["city_ibge_code"] == 5221700][["date", "new_confirmed"]].head() # Example to fix: 5221601,5221809

codes = clean_df[["city_ibge_code", "state"]].drop_duplicates()
count_confirmed = count_deaths = 0
variables = ["new_confirmed", "new_deaths"]
for index, row in codes.iterrows():
    subset = clean_df[(clean_df["city_ibge_code"] == row["city_ibge_code"]
                       ) & (clean_df["state"] == row["state"])].sort_values("date")
    for var in variables:
        if (len(subset) > 1):
            if (subset[var].iloc[0] == -subset[var].iloc[1]) & (subset[var].iloc[0] != 0):
                for i in range(2):
                    covid_munic.loc[(covid_munic["date"] == subset['date'].iloc[i]) &
                        (covid_munic["city_ibge_code"] == row["city_ibge_code"]) &
                        (covid_munic["state"] == row["state"]), [var]] = 0
                if var =="new_confirmed":
                    count_confirmed += 1
                elif var == "new_deaths":
                    count_deaths += 1

# Now Fixing the cumulative sum
covid_munic["last_available_confirmed"] = covid_munic.groupby(["city_ibge_code", "state"])["new_confirmed"].cumsum()
covid_munic["last_available_deaths"] = covid_munic.groupby(["city_ibge_code", "state"])["new_deaths"].cumsum()

min_date_no_rep = covid_munic[(covid_munic["new_confirmed"] != 0) | (covid_munic["new_deaths"] != 0
                )].groupby(["city_ibge_code", "state"])["date"].min().reset_index()
min_date_no_rep.columns = ["city_ibge_code", "state", "min_date_with_data"]

# Checking the data that it's not the same
# min_date = covid_munic.groupby(["city_ibge_code", "state"])["date"].min().reset_index()
# df = pd.merge(min_date, min_date_no_rep, how="left", on=["city_ibge_code", "state"])
# df.columns = ["city_ibge_code", "state", "min_date", "min_date_with_data"]
# check = covid_munic[covid_munic["city_ibge_code"].isin(df[df["min_date"] != df["min_date_with_data"]]["city_ibge_code"]) ]

# Excluding cases where there was no case in the beginning
clean_df = pd.merge(covid_munic, min_date_no_rep, on=["city_ibge_code", "state"])
covid_munic = clean_df[clean_df["date"] >= clean_df["min_date_with_data"]].drop(["min_date_with_data"], axis=1)


# Adding our fixes to our notes
notes.append("\n\nNumber of cases that we fixed the first updates (when it's 5 cases, but next update is -5 for example)")
notes.append("\nConfirmed: {} \nDeaths: {}".format(count_confirmed, count_deaths))
notes.append("\n\nNumber of rows where first rows were 0 cases or 0 deaths")
notes.append("\n{} rows".format(len(clean_df) - len(covid_munic)))



# Adding indicators
indicators = pd.read_csv("data\IndicadoresSociais_mun_distance.csv")
indicators.drop(["tipo", "UF", "population2019"], axis=1, inplace=True)
indicators.rename(columns={"codigo_ibge": "city_ibge_code", "nome": "name", "Região":"Region", "codigo_uf": "code_state"}, inplace=True)

# Taking out the variables from our main file so we can merge again
columns_to_drop = set(indicators.columns.values.tolist()) - set(['city_ibge_code'])
covid_munic.drop(list(columns_to_drop), axis=1, inplace=True)

merged = pd.merge(covid_munic, indicators, how='left', on='city_ibge_code',
         copy=True, indicator=False, validate=None)

# Fix some city names
merged.loc[merged["city_ibge_code"] == 1708254,['city']] = "Fortaleza do Tabocão"
merged.loc[merged["city_ibge_code"] == 2802601,["city"]] = "Gracho Cardoso"
merged.loc[merged["city_ibge_code"] == 2405306,["name"]] = "Januário Cicco"
merged.loc[merged["city_ibge_code"] == 2512606,["name"]] = "Quixaba"
merged.loc[merged["city_ibge_code"] == 2613107,["name"]] = "São Caitano"
merged.loc[merged["city_ibge_code"] == 2918803,["name"]] = "Laje"
merged.loc[merged["city_ibge_code"] == 2918902,["name"]] = "Lajedão"
merged.loc[merged["city_ibge_code"] == 2919058,["name"]] = "Lajedo do Tabocal"
merged.loc[merged["city_ibge_code"] == 4215695,["name"]] = "Santa Terezinha do Progresso"

# Put health region as "Não há" for states
merged.loc[merged["place_type"] == "state",["health_region"]] = "Estado"
merged.loc[merged["city"] == "Importados/Indefinidos",["health_region"]] = "Sem informação"

# Checks on indicators
# Any cities have different names (We are missing states names in Brasil.io, so using from indicators)
notes.append("\n\nCity names different from Brasil.io and Indicadores")
notes.append(merged[(merged["city"] != merged["name"]) & (merged["place_type"] == "city")
    & (merged["city"] != "Importados/Indefinidos")][["city_ibge_code","city",
    "name"]].groupby(["city_ibge_code","city", "name"]).count())
#Missing any info from Indicators
notes.append("\n\nMissing any info in Indicadores? We already know that Importados/Indefinidos don't have ibge_code")
notes.append(merged[(merged['name'].isnull()) & (merged['city'] != 'Importados/Indefinidos')].groupby(["place_type", "city"])["state"].count())


# Clean the merged file and put it into a file
merged.to_csv("data\caso_full_with_indicators.csv", index=False, encoding='utf-8-sig')


# Now let's put the notes into a file
notes.append("\n\nFinal Columns")
notes.append(merged.columns)

with open('data\load_brasilio_notes.csv', 'w', newline='\n', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    for row in zip(notes):
        writer.writerow(row)

