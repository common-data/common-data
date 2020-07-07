# ######################################################
# This code is to transfor data from view_source below to csv
# view-source:http://www.lixoes.cnm.org.br/principal/carrega_mapa_diagnostico
# view-source:http://www.desastres.cnm.org.br/principal/carrega_mapa_desastres
# ######################################################

import pandas as pd

# Getting our current data
lixao = pd.read_json("data\observatorio_dos_lixoes.json")

lixao.columns
# 'id', 'ibge', 'municipio', 'uf', 'estado',
vars = ['planos_municipais',
       'destinacao_final', 'tipo_destinacao', 'possui_coleta_seletiva',
       'coleta_participa_catadores', 'possui_catadores_regularizados',
       'realizam_compostagem', 'participam_consorcio']

# Check values
for var in vars:
    print(lixao[var].value_counts())

# Fix blanks to NA and other minor

for var in vars:
    lixao[var] = lixao[var].apply(lambda x: 'Nulo' if x == '' else x)

for var in ['realizam_compostagem', 'possui_catadores_regularizados', 'possui_coleta_seletiva']:
    lixao[var] = lixao[var].apply(lambda x: 'Não soube informar' if x == 'Não soube in' else x)

lixao['planos_municipais'] = lixao['planos_municipais'].apply(lambda x: 'Não soube informar' if x == 'Não Soube Infor' else x)


# Save into file
lixao.to_csv("data\observatorio_do_lixao.csv", index=False, encoding='utf-8-sig')







desastre = pd.read_json("data\observatorio_dos_desastres.json")
desastre_dec = pd.read_json("data\observatorio_dos_desastres_decretos.json")

desastre.columns
# 'mapas_desastres', 'tipo_desastre', 'vigencia', 'ibge', 'uf'
desastre_dec.columns
# 'id', 'id_municipio', 'municipio', 'uf', 'ibge', 'ano',
#        'mapas_desastres', 'tipo_desastre', 'total_decretos', 'det_ano',
#        'det_desastres', 'det_tipo'
print("Rows in desastre: {}; Rows in desastre decreto: {}".format(len(desastre), len(desastre_dec)))
# Rows in desastre: 5308; Rows in desastre decreto: 3616

# Check values
for var in desastre.columns:
    if desastre[var].nunique() <= 10:
        print(desastre[var].value_counts())
    else:
        print("var", var, desastre[var].nunique())

for var in desastre_dec.columns:
    if desastre_dec[var].nunique() <= 10:
        print(desastre_dec[var].value_counts())
    else:
        print("var", var, desastre_dec[var].nunique())

# ano is only unique values from det_vars, so let's remove them
del desastre_dec["ano"], desastre_dec["mapas_desastres"], desastre_dec["tipo_desastre"]

# Save into file
desastre.to_csv("data\observatorio_do_desastre.csv", index=False, encoding='utf-8-sig')
desastre_dec.to_csv("data\observatorio_do_desastre_decreto.csv", index=False, encoding='utf-8-sig')
