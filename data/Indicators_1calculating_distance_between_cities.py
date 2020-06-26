########################################################
# Adding distance between UF capital and nearest capital
# Also to nearest city with 150k+
########################################################

import pandas as pd
from datetime import date
import numpy as np
import os

def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """  Slightly modified version: of http://stackoverflow.com/a/29546836/2901002
    Calculate the great circle distance between two points on Earth (specified in decimal degrees or in radians)
    All (lat, lon) coordinates must have numeric dtypes and be of equal length.
    """
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2

    return (earth_radius * 2 * np.arcsin(np.sqrt(a))).round(2)


path = "\\".join(os.getcwd().split("\\"))
path

# Data with latitude and longitude
indicators = pd.read_excel("IndicadoresSociais_mun.xlsx")
indicators.drop(["nome.1", "latitude.1", "longitude.1", "tipo.1", "Região.1", "codigo_uf.1"], axis = 1, inplace = True)

indicators.head()

# Data with population
population = pd.read_csv("populacao-estimada-2019.csv")
population.rename(columns={"city_ibge_code": "codigo_ibge"}, errors="raise", inplace=True)
indicators["population2019"] = indicators.merge(population, how="left", on="codigo_ibge")["estimated_population"]

# Creating one dataframe for cities and other for all capitals and another for cities > 150000 (~200)
cities = indicators[indicators["tipo"] != "Estado"][['codigo_ibge', 'nome', 'latitude', 'longitude', 'UF']]
capitals = indicators[indicators["tipo"] == "Capital"][['UF', 'nome', 'latitude', 'longitude']]
capitals.columns = ['uf_capital', 'capital', 'lat_cap', 'long_cap']
cities150000 = indicators[indicators["population2019"] > 150000][['codigo_ibge', 'nome', 'latitude', 'longitude', 'UF']]
cities150000.columns = ['codigo_ibge_bigcity', 'bigcity', 'lat_bigcity', 'long_bigcity', "uf_bigcity"]

# Merging city with capital and big city
cities_capitals = cities.assign(key=1).merge(capitals.assign(key=1), on='key').drop('key', 1)
cities_bigcities = cities.assign(key=1).merge(cities150000.assign(key=1), on='key').drop('key', 1)

#Calculating the distance to Capital
cities_capitals['distance_capital'] = \
    haversine(cities_capitals['latitude'], cities_capitals['longitude'],
              cities_capitals['lat_cap'], cities_capitals['long_cap'])

#Calculating the distance to Big city (it can be the capital)
cities_bigcities['distance_nearest_bigcity'] = \
    haversine(cities_bigcities['latitude'], cities_bigcities['longitude'],
              cities_bigcities['lat_bigcity'], cities_bigcities['long_bigcity'])

# Getting the minimum distances
distance_capital = cities_capitals[cities_capitals["UF"] == cities_capitals["uf_capital"]][["codigo_ibge", "distance_capital"]]
distance_nearest_capital = cities_capitals.groupby("codigo_ibge")["distance_capital"].min().reset_index()
distance_nearest_bigcity = cities_bigcities.groupby("codigo_ibge")["distance_nearest_bigcity"].min().reset_index()

#Changing the name of column to final column we want
distance_nearest_capital.columns = ["codigo_ibge", "distance_nearest_capital"]


# Merging back to indicators
indicators = pd.merge(indicators, distance_capital, how='left', on="codigo_ibge")\
    .merge(distance_nearest_capital, on="codigo_ibge")\
    .merge(distance_nearest_bigcity, on="codigo_ibge")

indicators.to_csv('IndicadoresSociais_mun_distance.csv', index=False, encoding='utf-8')