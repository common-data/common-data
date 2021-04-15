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


def cleaning_beginning(dataset, count_confirmed=0, count_deaths=0, count_cleaning=0):
    # Cities that had positive on first day and then negative on next update, let's transform both to zero
    clean_df = covid_munic[(covid_munic["new_confirmed"] != 0) | (covid_munic["new_deaths"] != 0)]
    # clean_df[clean_df["city_ibge_code"] == 5221700][["date", "new_confirmed"]].head() # Example to fix: 5221601,5221809

    codes = clean_df[["city_ibge_code", "state"]].drop_duplicates()
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
                    if var == "new_confirmed":
                        count_confirmed += 1
                    elif var == "new_deaths":
                        count_deaths += 1
                    print(subset[["city_ibge_code", "state", "date", var, "order_for_place"]].iloc[0:2])

    min_date_no_rep = covid_munic[(covid_munic["new_confirmed"] != 0) | (covid_munic["new_deaths"] != 0
                                                                         )].groupby(["city_ibge_code", "state"])[
        "date"].min().reset_index()
    min_date_no_rep.columns = ["city_ibge_code", "state", "min_date_with_data"]

    # Excluding cases where there was no case in the beginning
    clean_df = pd.merge(covid_munic, min_date_no_rep, on=["city_ibge_code", "state"])
    final_df = clean_df[clean_df["date"] >= clean_df["min_date_with_data"]].drop(["min_date_with_data"], axis=1)
    count_cleaning = count_cleaning + len(clean_df) - len(final_df)
    return count_confirmed, count_deaths, count_cleaning, final_df


# Setting the variables
notes = []
results = []
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Getting full file from Brasil.io
url = 'https://data.brasil.io/dataset/covid19/caso_full.csv.gz'
r = requests.get(url, allow_redirects=True)
open('common_data\data\caso_full.csv.gz', 'wb').write(r.content)
covid_munic = pd.read_csv('common_data\data\caso_full.csv.gz', compression='gzip', delimiter=",",
                 quotechar='"', lineterminator="\n").sort_values(["date", "city_ibge_code"])

# Add number of lines to not
notes.append("Brasil.IO has {} rows".format(len(covid_munic)))

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
count_confirmed = count_deaths = count_cleaning = 0
check_cleaning = 1
while check_cleaning != count_cleaning:
    check_cleaning = count_cleaning
    count_confirmed, count_deaths, count_cleaning, covid_munic = cleaning_beginning(covid_munic, count_confirmed, count_deaths, count_cleaning)
    print(count_confirmed, count_deaths, count_cleaning)

# Adding our fixes to our notes
notes.append("\n\nNumber of cases that we fixed the first updates (when it's 5 cases, but next update is -5 for example)")
notes.append("\nConfirmed: {} \nDeaths: {}".format(count_confirmed, count_deaths))
notes.append("\n\nNumber of rows where first rows were 0 cases or 0 deaths")
notes.append("\n{} rows".format(count_cleaning))



# Now Fixing some data
covid_munic["last_available_confirmed"] = covid_munic.groupby(["city_ibge_code", "state"])["new_confirmed"].cumsum()
covid_munic["last_available_deaths"] = covid_munic.groupby(["city_ibge_code", "state"])["new_deaths"].cumsum()
covid_munic["order_for_place"] = covid_munic.groupby(["city_ibge_code", "state"])["date"].cumcount() + 1
covid_munic["last_available_death_rate"] = (covid_munic["last_available_deaths"] / covid_munic["estimated_population_2019"])
covid_munic["last_available_confirmed_per_100k_inhabitants"] = (covid_munic["last_available_confirmed"] / covid_munic["estimated_population_2019"] * 100000)

covid_munic = covid_munic[(covid_munic["order_for_place"] == 1) | (covid_munic["order_for_place"] % 7 == 0) | covid_munic["is_last"]]
covid_munic["new_confirmed"] = covid_munic.groupby(["city_ibge_code", "state"])["last_available_confirmed"].diff()
covid_munic["new_deaths"] = covid_munic.groupby(["city_ibge_code", "state"])["last_available_deaths"].diff()
covid_munic.loc[covid_munic["order_for_place"] == 1,['new_confirmed']] = covid_munic[covid_munic["order_for_place"] == 1]['last_available_confirmed']
covid_munic.loc[covid_munic["order_for_place"] == 1,['new_deaths']] = covid_munic[covid_munic["order_for_place"] == 1]['last_available_deaths']



# Adding indicators
indicators = pd.read_csv("common_data\data\outras\IndicadoresSociais_mun_distance.csv")
indicators.drop(["tipo", "UF",'POP_DOU','POP_TCU', 'POP', 'Primeiro_Confirmado','Status_COVID','RANK_g100','Amazonia_Legal', 'Semiarido', 'Nota_1','Atividade_Maior_Valor_Adicionado_Bruto', 'Primeira_Morte','CidadeRegiao_SP','PIB_per_capita_precos_correntes1', 'Indicador_3_Obrigacoes_FinanceirasDisponibilidadeCaixa', 'Valor_adicionado_bruto_AdministracaoDefesaEducacaoSaudePublicasSeguridadeSocial_precos_correntes1000', 'ImpostosLiquidosSubsidiosSobreProdutos_precos_correntes1000','Valor_adicionado_bruto_Servicos_preços_correntes1000_exceto_AdministracaoDefesaEducacaoSaudePublicasSeguridadeSocial','POP_DOU','POP_TCU','ID_g100','Valor_adicionado_bruto_Industria_precos_correntes1000','Valor_adicionado_bruto_total_precos_correntes1000','Valor_adicionado_bruto_Agropecuaria_precos_correntes1000','Classificacao_CAPAG','Total_inadimplencias','PIB2017_precos_correntes1000','Nota_3','Classificacao_CAUC','Nota_2','Indicador_1_Endividamento','CAPACxCAUC','Indicador_2_PoupancaCorrente'], axis=1, inplace=True)
indicators.rename(columns={"codigo_ibge": "city_ibge_code", "nome": "name", "Região":"Region", "codigo_uf": "code_state"}, inplace=True)

merged = pd.merge(covid_munic, indicators, how='left', on='city_ibge_code',
         copy=True, indicator=False, validate=None)

# Fix some city names
merged.loc[merged["city_ibge_code"] == 1708254,['city']] = "Fortaleza do Tabocão"
merged.loc[merged["city_ibge_code"] == 2405306,["name"]] = "Januário Cicco"
merged.loc[merged["city_ibge_code"] == 2512606,["name"]] = "Quixaba"
merged.loc[merged["city_ibge_code"] == 2613107,["name"]] = "São Caitano"
merged.loc[merged["city_ibge_code"] == 2802601,["city"]] = "Gracho Cardoso"
merged.loc[merged["city_ibge_code"] == 2918753,["name"]] = "Lagoa Real"
merged.loc[merged["city_ibge_code"] == 2918803,["name"]] = "Laje"
merged.loc[merged["city_ibge_code"] == 2918902,["name"]] = "Lajedão"
merged.loc[merged["city_ibge_code"] == 2919009,["name"]] = "Lajedinho"
merged.loc[merged["city_ibge_code"] == 2919058,["name"]] = "Lajedo do Tabocal"
merged.loc[merged["city_ibge_code"] == 3122900,["name"]] = "Dona Euzébia"
merged.loc[merged["city_ibge_code"] == 4215687,["name"]] = "Santa Terezinha do Progresso"
merged.loc[merged["city_ibge_code"] == 4215695,["name"]] = "Santiago do Sul"

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
filename = "caso_full_with_indicators"
compression_options = dict(method='zip', archive_name=f'{filename}.csv')
merged.to_csv(f"common_data\data\{filename}.zip", compression = compression_options, index=False, encoding='utf-8-sig')


# Now let's put the notes into a file
notes.append("\n\nFinal Columns")
notes.append(merged.columns)

with open('common_data\data\load_brasilio_notes.csv', 'w', newline='\n', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    for row in zip(notes):
        writer.writerow(row)

