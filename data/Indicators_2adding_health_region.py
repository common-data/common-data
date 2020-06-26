########################################################
# Adding health region to cities
########################################################

import pandas as pd
import os


path = "\\".join(os.getcwd().split("\\"))
path

# Full data
indicators = pd.read_csv("data\IndicadoresSociais_mun_distance.csv")
indicators["city_ibge_code"] = indicators["codigo_ibge"].apply(lambda x: int(str(x)[:-1]) if len(str(x)) > 6 else x)
indicators[["city_ibge_code", "codigo_ibge"]].nunique()
indicators.head()


# Data with health region
health_region = pd.read_excel("data\\regionais de saude.xls", skiprows=2)
health_region.columns = ['UF', 'health_region_name', "name", "city_ibge_code"]

# Add health region
indicators["health_region"] = pd.merge(indicators, health_region, how="left", on="city_ibge_code")["health_region_name"]

# Checking which is without a health region: 5
indicators[indicators["health_region"].isnull()][["codigo_ibge", "city_ibge_code", "nome", "UF"]]

# Fixing them after some research
indicators.loc[indicators["city_ibge_code"] == 431454, "health_region"] = "CRS 05 Caxias do Sul"
indicators.loc[indicators["city_ibge_code"] == 500627, "health_region"] = "NCT de Campo Grande"
indicators.loc[indicators["city_ibge_code"] == 150475, "health_region"] = "Baixo Amazonas"
indicators.loc[indicators["city_ibge_code"] == 421265, "health_region"] = "Tubarão"
indicators.loc[indicators["city_ibge_code"] == 422000, "health_region"] = "Criciúma"

# Checking which is without a health region: now we have none
indicators[indicators["health_region"].isnull()][["codigo_ibge", "city_ibge_code", "nome", "UF"]]


# Saving back to same CSV file, but now with this info
indicators.drop("city_ibge_code", axis=1, inplace=True)
indicators.to_csv('data\IndicadoresSociais_mun_distance.csv', index=False, encoding='utf-8')