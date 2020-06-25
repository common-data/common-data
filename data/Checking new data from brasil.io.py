# We were getting the whole data everyday, but Brasil.io had limited the API calls (they are free, we understand and
# still love them!), but then we had to get less data.
# This file is to check how the data changes between 2 updates, considering the numbers of confirmed and deaths
# and also the new rows in our full data file (considering a row = date + city_ibge_code


import pandas as pd
import os
import inspect

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(path)

# Adding indicators
new_file = pd.read_csv("data\caso_full_with_indicators.csv")
previous_file = pd.read_csv("data\caso_full_with_indicators_20200622.csv")

new_file['last_available_date'].value_counts().sort_values()

new_file.drop(['epidemiological_week', 'estimated_population_2019', 'is_last', 'is_repeated',
        'order_for_place', 'name',
       'latitude', 'longitude', 'Region', 'code_state', 'RAZDEP', 'GINI',
       'PIND', 'PMPOB', 'PPOB', 'RDPC', 'T_AGUA', 'T_BANAGUA', 'T_DENS',
       'AGUA_ESGOTO', 'T_RMAXIDOSO', 'IDHM', 'IDHM_E', 'IDHM_L', 'IDHM_R',
       'distance_capital', 'distance_nearest_capital',
       'distance_nearest_bigcity'], axis= 1, inplace=True)
previous_file.drop(['epidemiological_week', 'estimated_population_2019', 'is_last', 'is_repeated',
        'order_for_place', 'name',
       'latitude', 'longitude', 'Region', 'code_state', 'RAZDEP', 'GINI',
       'PIND', 'PMPOB', 'PPOB', 'RDPC', 'T_AGUA', 'T_BANAGUA', 'T_DENS',
       'AGUA_ESGOTO', 'T_RMAXIDOSO', 'IDHM', 'IDHM_E', 'IDHM_L', 'IDHM_R',
       'distance_capital', 'distance_nearest_capital',
       'distance_nearest_bigcity'], axis= 1, inplace=True)

new_file["city_ibge_code"] = new_file["city_ibge_code"].fillna(99)
previous_file["city_ibge_code"] = previous_file["city_ibge_code"].fillna(99)
print(len(new_file), len(previous_file))
# 248421 243344

together = new_file.merge(previous_file, how="inner", on=["city_ibge_code", "date", "state"])
print(len(together))
# 243344

for var in together.columns:
    if len(together[together[var].isnull()]) > 0:
        print(var, len(together[together[var].isnull()]))
# city_x 2731
# last_available_confirmed_per_100k_inhabitants_x 7352
# city_y 2731
# last_available_confirmed_per_100k_inhabitants_y 7354
together = together.fillna(0)


columns = ['last_available_confirmed', 'last_available_confirmed_per_100k_inhabitants',
       'last_available_death_rate', 'last_available_deaths', 'new_confirmed', 'new_deaths',
       'place_type']

for var in columns:
    var_new = var + "_x"
    var_previous = var + "_y"
    # print(len(together[together[var_new] != together[var_previous]]))
    if len(together[together[var_new] != together[var_previous]]) > 0:
        print(together[[var_new, var_previous]].describe())
        print(together[together[var_new] != together[var_previous]][[var_new, var_previous]].describe())


diffs = together[(together['last_available_confirmed_x'] != together['last_available_confirmed_y']
          ) | (together['last_available_confirmed_per_100k_inhabitants_x'] != together['last_available_confirmed_per_100k_inhabitants_y']
          ) | (together['last_available_death_rate_x'] != together['last_available_death_rate_y']
          ) | (together['new_confirmed_x'] != together['new_confirmed_y']
          ) | (together['new_deaths_x'] != together['new_deaths_y']
          )].sort_values(['city_ibge_code', 'date'])

print(len(diffs)) #1284
print(diffs['date'].value_counts().sort_values())
# 2020-06-19    134
# 2020-06-20    301
# 2020-06-21    849
print(diffs['place_type_x'].value_counts().sort_values())
# state       6
# city     1278


# Considering only the new rows, but not considering the day after (we wouldn't have it on this data anyway)
only_new = new_file[new_file['date'] < '2020-06-22'].merge(previous_file, how="left", on=["city_ibge_code", "date", "state"])
only_new = only_new[(only_new["new_confirmed_y"].isnull())]
print(len(only_new)) #86
print(only_new['city_ibge_code'].unique())
# 1301803. 2901155. 5007307. 4102109. 4107538. 4108957. 4110607. 4111555.
#  4111704. 4112603. 4117255. 4120358. 4121109. 4126306. 2405900. 2413557
print(only_new[only_new["last_available_confirmed_x"] != 0 ]['date'].value_counts())
# 2020-06-21    14
# 2020-06-20    11
# 2020-06-19     2
print(only_new[only_new["new_confirmed_x"] != 0 ]['date'].value_counts())
# 2020-06-20    9
# 2020-06-21    5
# 2020-06-19    2
print(only_new[only_new["last_available_deaths_x"] != 0 ]['date'].value_counts()) #None
print(only_new[only_new["new_deaths_x"] != 0 ]['date'].value_counts()) #None




# Conclusion:
# We only compared 2 days (23 and 22/06), but it was only the last 3 days that had differences from the day before.
# Considering the new rows [date, citi_ibge_code], we had some dates prior that were added, but they were cities
# with no cases at the time.
# So we decided to get only the last 14 days of data to have a bigger window there,
# specially because we have compared only 2 days on this analysis.