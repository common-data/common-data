# Dicionário de variáveis

Esse documento visa apresentar os dados do arquivo `caso_full_with_indicators.csv`. As fontes de dados utilizadas foram:
- `caso_full` do projeto [Brasil.io](https://brasil.io/home/) usando Secretarias de Saúde das Unidades Federativas como fonte e com dados tratados por Álvaro Justen
e colaboradores;
-  [Atlas do IDH-M](http://atlasbrasil.org.br/2013/).

Ao fim da junção dos dados acima, é criado o arquivo `load_brasilio_notes.csv` com notas gerais com as seguintes informações:
- Número de linhas
- Último dia dos dados
- Se alguma coluna foi adicionada ou excluida do processo atual
- Números totais de casos Covid-19 confirmados, mortes e população
- Número de UFs nos ultimos 10 dias de dados (as SES nao atualizam todos os dias)
- Cidades com nomes diferentes entre Brasil.io e indicadores
- Cidades com informação faltante em indicadores
- Colunas finais (listadas abaixo)

As colunas finais são:
####[Brasil.io](https://github.com/turicas/covid19-br/blob/master/api.md#caso_full)
- `city`: nome do município (pode estar em branco quando o registro é
  referente ao estado, pode ser preenchido com `Importados/Indefinidos`
  também).
- `city_ibge_code`: código IBGE do local.
- `date`: data de coleta dos dados no formato YYYY-MM-DD.
- `epidemiological_week`: número da semana epidemiológica.
- `estimated_population_2019`: população estimada para esse município/estado em
  2019, segundo o IBGE.
- `is_last`: campo pré-computado que diz se esse registro é o mais novo para
  esse local, pode ser `True` ou `False` (caso filtre por esse campo, use
  `is_last=True` ou `is_last=False`, **não use o valor em minúsculas**).
- `is_repeated`: campo pré-computado que diz se as informações nesse
  registro foram publicadas pela Secretaria Estadual de Saúde no dia `date` ou
  se o dado é repetido do último dia em que o dado está disponível (igual ou
  anterior a `date`). Isso ocorre pois nem todas as secretarias publicam
  boletins todos os dias. Veja também o campo `last_available_date`.
- `last_available_confirmed`: número de casos confirmados do último dia
  disponível igual ou anterior à data `date`.
- `last_available_confirmed_per_100k_inhabitants`: número de casos confirmados
  por 100.000 habitantes do último dia disponível igual ou anterior à data
  `date`.
- `last_available_date`: data da qual o dado se refere.
- `last_available_death_rate`: taxa de mortalidade (mortes / confirmados) do
  último dia disponível igual ou anterior à data `date`.
- `last_available_deaths`: número de mortes do último dia disponível igual ou
  anterior à data `date`.
- `order_for_place`: número que identifica a ordem do registro para este
  local. O registro referente ao primeiro boletim em que esse local aparecer
  será contabilizado como `1` e os demais boletins incrementarão esse valor.
- `place_type`: tipo de local que esse registro descreve, pode ser `city` ou
  `state`.
- `state`: sigla da unidade federativa, exemplo: SP.
- `new_confirmed`: número de novos casos confirmados desde o último dia (note
  que caso `is_repeated` seja `True`, esse valor sempre será `0` e que esse
  valor pode ser negativo caso a SES remaneje os casos desse município para
  outro).
- `new_deaths`: número de novos óbitos desde o último dia (note que caso
  `is_repeated` seja `True`, esse valor sempre será `0` e que esse valor pode
  ser negativo caso a SES remaneje os casos desse município para outro).
 
 ####Atlas:
- `name`: nome do municipio ou estado
- `latitude`: latitude central do municipio/UF
- `longitude`: longitude central do municipio/UF
- `Region`: regiao brasileira
- `code_state`: primeiros 2 digitos do codigo IBGE, sendo referentes a UF
- `RAZDEP`: razão de dependência = percentual da população de menos de 15 anos e de 65 anos ou mais em relação à população de 15 a 64 anos
- `GINI`: Índice de Gini
- `PIND`: proporção de extremamente pobres = percentual dos indivíduos com renda domiciliar per capita igual ou inferior a R$ 70,00 mensais em agosto de 2010. O universo de indivíduos é limitado àqueles que vivem em domicílios particulares permanentes.
- `PMPOB`: propoção de pobres = percentual dos indivíduos com renda domiciliar per capita igual ou inferior a R$ 140,00 mensais, em reais de agosto de 2010. O universo de indivíduos é limitado àqueles que vivem em domicílios particulares permanentes.
- `PPOB`: proporção de vulneráveis à pobreza = percentual dos indivíduos com renda domiciliar per capita igual ou inferior a R$ 255,00 mensais, em reais de agosto de 2010, equivalente a 1/2 salário mínimo nessa data. O universo de indivíduos é limitado àqueles que vivem em domicílios particulares permanentes.
- `RDPC`: renda domiciliar per capita
- `T_AGUA`: percentual da população que vive em domicílios com água encanada
- `T_BANAGUA`: percentual da população que vive em domicílios com banheiro e água encanada
- `T_DENS`: percentual da população que vive em domicílios com densidade superior a 2 pessoas por dormitório
- `AGUA_ESGOTO`: percentual de pessoas em domicílios com abastecimento de água e esgotamento sanitário inadequados
- `T_RMAXIDOSO`: percentual de pessoas em domicílios vulneráveis à pobreza e dependentes de idosos = razão entre as pessoas que vivem em domicílios vulneráveis à pobreza (com renda per capita inferior a 1/2 salário mínimo de agosto de 2010) e nos quais a principal fonte de renda provém de moradores com 65 anos ou mais de idade e população total residente em domicílios particulares permanentes multiplicado por 100
- `IDHM`: Índice de Desenvolvimento Humano Municipal é uma medida composta de indicadores de três dimensões do desenvolvimento humano: longevidade, educação e renda. O índice varia de 0 a 1. Quanto mais próximo de 1, maior o desenvolvimento humano 
- `IDHM_E`: a parte da educação do IDHM 
- `IDHM_L`: a parte da longevidade do IDHM
- `IDHM_R`: a parte da renda do IDHM

 ####Distância entre cidades (calculating_distance_between_cities.py):
- `distance_capital`: distância, em km, entre a cidade e a capital da UF
- `distance_nearest_capital`: minima distância, em km, entre a cidade e uma capital
- `distance_nearest_bigcity`: minima distância, em km, entre a cidade e uma cidade de mais de 150 mil habitantes
