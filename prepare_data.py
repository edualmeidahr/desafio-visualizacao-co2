"""
Preparação dos dados para o app "Quem aquece o planeta?".

Entrada : data/owid-co2-data.csv  (dataset original do Our World in Data)
Saídas  : data/co2_paises.csv     (apenas países, 1950-2024, colunas selecionadas)
          data/co2_mundo.csv      (agregado "World", 1950-2024)

Para rodar:  python prepare_data.py

Ajustes realizados (todos pequenos, sem alterar nenhum valor):
  1. Baixa o CSV original caso ele ainda não exista em data/.
  2. Separa países de agregados: no dataset, regiões e grupos ("World", "Africa",
     "High-income countries", "European Union (27)"...) não têm código ISO.
     Mantemos só as linhas com iso_code preenchido (países e territórios).
  3. Recorta o período 1950-2024: antes de 1950 a cobertura por país é bem menor.
     As colunas "acumuladas" já vêm calculadas pela fonte desde o início da série,
     então o recorte NÃO muda os valores acumulados.
  4. Seleciona apenas as colunas usadas nas visualizações e renomeia para português.
  5. Cria a coluna "pais" com o nome em português para os países mais citados.
  6. Valores faltantes NÃO são preenchidos nem inventados: ficam vazios e cada
     gráfico simplesmente ignora o país/ano sem dado.
"""

from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

PASTA_DADOS = Path(__file__).parent / "data"
ARQUIVO_ORIGINAL = PASTA_DADOS / "owid-co2-data.csv"
URL_ORIGINAL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"

ANO_INICIAL = 1950

# Colunas originais -> nomes em português (unidades conforme o codebook da OWID)
COLUNAS = {
    "country": "country",                                # nome original (inglês)
    "iso_code": "iso_code",                              # código ISO de 3 letras
    "year": "ano",
    "population": "populacao",
    "co2": "co2",                                        # Mt de CO₂ fóssil + indústria
    "co2_per_capita": "co2_per_capita",                  # t de CO₂ por pessoa
    "land_use_change_co2": "co2_uso_terra",              # Mt de CO₂ de mudança no uso da terra
    "co2_including_luc": "co2_com_uso_terra",            # Mt (fóssil + uso da terra)
    "cumulative_co2": "co2_acumulado",                   # Mt acumulado (fóssil)
    "cumulative_co2_including_luc": "co2_acumulado_com_uso_terra",
    "share_global_cumulative_co2": "parcela_acumulado",                  # % do mundo
    "share_global_cumulative_co2_including_luc": "parcela_acumulado_com_uso_terra",
}

# Tradução dos nomes de países que aparecem com destaque nos gráficos.
# Os demais continuam com o nome original em inglês.
NOMES_PT = {
    "Brazil": "Brasil", "United States": "Estados Unidos", "China": "China",
    "India": "Índia", "Russia": "Rússia", "Germany": "Alemanha",
    "United Kingdom": "Reino Unido", "Japan": "Japão", "France": "França",
    "Canada": "Canadá", "Indonesia": "Indonésia", "Ukraine": "Ucrânia",
    "Mexico": "México", "Iran": "Irã", "Saudi Arabia": "Arábia Saudita",
    "South Korea": "Coreia do Sul", "Italy": "Itália", "Poland": "Polônia",
    "Australia": "Austrália", "South Africa": "África do Sul",
    "Turkey": "Turquia", "Argentina": "Argentina", "Spain": "Espanha",
    "Qatar": "Catar", "Kuwait": "Kuwait", "United Arab Emirates": "Emirados Árabes Unidos",
    "Bahrain": "Bahrein", "Democratic Republic of Congo": "República Democrática do Congo",
    "Nigeria": "Nigéria", "Pakistan": "Paquistão", "Bangladesh": "Bangladesh",
    "Vietnam": "Vietnã", "Thailand": "Tailândia", "Egypt": "Egito",
    "Kazakhstan": "Cazaquistão", "Malaysia": "Malásia", "Colombia": "Colômbia",
    "Peru": "Peru", "Bolivia": "Bolívia", "Paraguay": "Paraguai",
    "Venezuela": "Venezuela", "Chile": "Chile", "Ethiopia": "Etiópia",
    "Philippines": "Filipinas", "Netherlands": "Países Baixos", "Taiwan": "Taiwan",
}


def preparar() -> None:
    # 1. Baixa o arquivo original, se necessário
    if not ARQUIVO_ORIGINAL.exists():
        PASTA_DADOS.mkdir(exist_ok=True)
        print(f"Baixando {URL_ORIGINAL} ...")
        urlretrieve(URL_ORIGINAL, ARQUIVO_ORIGINAL)

    bruto = pd.read_csv(ARQUIVO_ORIGINAL)
    print(f"Dataset original: {bruto.shape[0]} linhas x {bruto.shape[1]} colunas, "
          f"anos {bruto['year'].min()}-{bruto['year'].max()}")

    # 3 e 4. Recorte de período e seleção/renomeação de colunas
    dados = bruto.loc[bruto["year"] >= ANO_INICIAL, list(COLUNAS)].rename(columns=COLUNAS)

    # Mantém apenas anos com algum dado de emissão (o arquivo pode trazer
    # linhas de anos futuros só com população projetada)
    tem_emissao = dados[["co2", "co2_com_uso_terra"]].notna().any(axis=1)
    ultimo_ano = dados.loc[tem_emissao, "ano"].max()
    dados = dados[dados["ano"] <= ultimo_ano]

    # 2. Separa países (têm ISO) do agregado mundial
    paises = dados[dados["iso_code"].notna()].copy()
    mundo = dados[dados["country"] == "World"].drop(columns=["iso_code"])

    # 5. Nome em português
    paises["pais"] = paises["country"].map(NOMES_PT).fillna(paises["country"])

    paises.to_csv(PASTA_DADOS / "co2_paises.csv", index=False)
    mundo.to_csv(PASTA_DADOS / "co2_mundo.csv", index=False)

    # Resumo para conferência (exploração rápida)
    print(f"Países: {paises['country'].nunique()} | anos {paises['ano'].min()}-{paises['ano'].max()} "
          f"| {len(paises)} linhas")
    print("\nPercentual de valores faltantes por coluna (países):")
    print((paises.isna().mean() * 100).round(1).to_string())
    print("\nEstatísticas do último ano:")
    print(paises[paises["ano"] == ultimo_ano][["co2", "co2_per_capita", "co2_uso_terra"]]
          .describe().round(2).to_string())


if __name__ == "__main__":
    preparar()
