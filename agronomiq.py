#! /usr/bin/python

# **************************************#
# -- coding: utf-8 --                   #
# **************************************#
# Author:                               #
# João Paulo Cardoso do Carmo           #
# Date: 2025-08-30                      #
# **************************************#

#*********** Imports ***********
import matplotlib.pyplot as plt
import branca.colormap as cm
from pathlib import Path
import geopandas as gpd
import seaborn as sns
import pandas as pd
import requests
import os

#*********** Path File ***********
THIS_PATH = Path(__file__).parent.absolute()

#*********** Methods ***********
def task_01():
    """
    Instruções:
        1- Download dos dados municipais do estado de Minas Gerais;
        2- Transformação dos dados de desmatamento;
        3- Processamento dos dados:
            -reprojeção para EPSG:31983;
            -cálculo de área;
        4- Geração dos arquivos de saída no formato GeoJSON;

    Observações
        - O Arquivo nã foi setado na mão o crs, e sim usado a função do próprio geopandas,
        pois deixa o código mais robusto.
        - Não foi salvo em UTM o arquivo, pois não é uma boa prática quando se usa geopandas e geojson.
    """
    
    # Read geojson 
    link_geojson = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-31-mun.json"
    gframe = gpd.read_file(link_geojson)
    # Explode file
    gframe = gframe.reset_index(drop=True).explode(ignore_index=True)

    # Find utm crs
    utm_crs = gframe.estimate_utm_crs()
    # Convert to UTM
    gframe = gframe.to_crs(utm_crs)
    # Calc área in km²
    gframe["area_km2"] = gframe.area / 1_000_000

    # Convert to 4326
    gframe = gframe.to_crs(4326)
    # Path to save
    path_output = os.path.join(THIS_PATH, "dados", "municipios-mg.geojson")
    # Save file
    gframe.to_file(path_output)

    # Output to user
    print(f"Task 01 done, file path: {path_output}")

def task_02():
    """
    - a) Procure uma fonte de dados confiável na internet de população e PIB dos municípios
    brasileiros e salve os dados de população e PIB dos municípios de Minas Gerais
    em um arquivo CSV com o nome dados/populacao-pib-municipios-mg.csv.
    
    - b) Utilize os dois arquivos de focos de desmatamento como base
    (dados/desmatamento_ago22.gpkg e dados/desmatamento_set_22.gpkg), 
    junte-os em um único dataset, transforme-o em um GeoJSON na projeção EPSG:31983 e
    salve-o em dados/focos-desmatamento-mg.geojson.

    - c) No notebook 02_analise.ipynb, faça uma análise exploratória dos dados,
     respondendo às seguintes perguntas:
        - c.1) Qual a área total desmatada em hectares no estado de Minas Gerais 
        em cada um dos meses de agosto e setembro de 2022?
        - c.2) Qual a área total desmatada em km² no estado de Minas Gerais em todo o
         período fornecido (ago/set de 2022) por bioma?
        - c.3) Qual a área total desmatada em km² no estado de Minas Gerais
         em cada um dos meses de agosto e setembro de 2022, por município?

    - d) No notebook 02_analise.ipynb faça uma análise de correlação entre as
    variáveis de população e PIB dos municípios de Minas Gerais e a área
    desmatada em hectares. Apresente os resultados da forma que achar mais adequada.
    """

    def a()->pd.DataFrame:
        # Path input
        path_input = os.path.join(THIS_PATH, "dados", "task_02", "ibge_mg.xlsx")
        # Reading file
        dataframe = pd.read_excel(path_input)
        #Filter columns
        dataframe = dataframe[["Município [-]", "PIB per capita - R$ [2021]", "População no último censo - pessoas [2022]"]]
        # Path to save
        path_output = os.path.join(THIS_PATH, "dados","populacao-pib-municipios-mg.csv")
        dataframe.to_csv(path_output)
        print(f"Caminho do csv: {path_output}") 

        return dataframe

    def b()->gpd.GeoDataFrame:
        """
        Observações:
        - O UTM não ficou harcode (31982), e sim usando a lib do geopandas que é mais robusta.
        - Foi salvo em UTM o arquivo pois exigia na task, porém NÃO é uma boa prática salvar
        geojson em UTM usando geopandas devido a problemas de versões.
        """
        # Base path
        base_dir = os.path.join(THIS_PATH, "dados")
        # Create master dataset
        master_dataset = gpd.GeoDataFrame(geometry=[], crs=4326)

        for file in os.listdir(base_dir):
            # Check ext
            if "gpkg" in file:
                # Get path file
                file_path = os.path.join(base_dir, file)
                # Read file
                gframe = gpd.read_file(file_path)
                # Add date
                if "ago" in file:
                    gframe["mes"] = "agosto"
                elif "set" in file:
                    gframe["mes"] = "setembro"

                # Join dataset
                master_dataset = pd.concat([master_dataset, gframe], ignore_index=True)
        
        # Find utm crs
        utm_crs = master_dataset.estimate_utm_crs()
        # Convert to UTM 
        master_dataset = master_dataset.to_crs(utm_crs)
        # Path to save
        file_path = os.path.join(THIS_PATH, "dados", "focos-desmatamento-mg.geojson")
        # Save geojson
        master_dataset.to_file(file_path)

        # Output to user
        print(f"Task 02, b) done, file path: {file_path}")
        return master_dataset

    def c(gframe:gpd.GeoDataFrame):
        # Convert to km² and remove geometry
        gframe["area_km2"] = gframe.area / 1e6
        gframe = gframe.drop(columns="geometry")

        # Filtering for August and September 2022
        gframe_august = gframe[gframe["mes"] == "agosto"]
        gframe_september = gframe[gframe["mes"] == "setembro"]

        # Total deforested area in August
        total_august = gframe_august["area_km2"].sum()
        print(f"Deforested area in August 2022: {total_august * 100} hectares")

        # Total deforested area in September
        total_september = gframe_september["area_km2"].sum()
        print(f"Deforested area in September 2022: {total_september  * 100} hectares")

        # Now, total deforested area by biome
        dataframe_biome = gframe.groupby("Bioma")["area_km2"].sum()
        print("\nTotal deforested area by biome (in km²):")
        print(dataframe_biome)

        # Now, total deforested area by municipality
        dataframe_municipality = gframe.groupby("NuFis")["area_km2"].sum()
        print("\nTotal deforested area by municipality (in km²):")
        print(dataframe_municipality)

    def d(dataframe_pib_population:pd.DataFrame, gframe_deforestation:gpd.GeoDataFrame):
        # Find deforestation by municipality
        path_full_municipality = os.path.join(THIS_PATH, "dados", "municipios-mg.geojson")
        # Read file
        municipality = gpd.read_file(path_full_municipality)
        # Convert to utm
        municipality = municipality.to_crs(gframe_deforestation.crs)
        # Explode file
        municipality = municipality.reset_index(drop=True).explode(ignore_index=True)

        # Create geodataframe with informations necessary
        date_by_city = gpd.GeoDataFrame(geometry=[], crs=municipality.crs)
        date_by_city.geometry = municipality.geometry
        date_by_city["municipio"] = municipality["name"]
        date_by_city["desmatamento_hectare"] = 0
        date_by_city["populacao"] = 0
        date_by_city["pib"] = 0
        
        # Drop var
        del municipality

        for i, city_area in date_by_city.iterrows():
            deforestation = gframe_deforestation[gframe_deforestation.intersects(city_area.geometry)]
            if deforestation.empty: continue
            # Add area deforestation into date_by_city
            date_by_city.at[i, "desmatamento_hectare"] = sum(deforestation.area / 1e4)
            # Find match with dataframe_pib_population
            match_city = dataframe_pib_population[dataframe_pib_population["Município [-]"] == city_area.municipio]
            if match_city.empty: continue
            date_by_city.at[i, "populacao"] = int(match_city["População no último censo - pessoas [2022]"].iloc[0])
            date_by_city.at[i, "pib"] = int(match_city["PIB per capita - R$ [2021]"].iloc[0])
        
        # Drop nan values
        date_by_city = date_by_city[(date_by_city != 0).all(axis=1)]
        # Get corr
        corr_matrix = date_by_city[["populacao", "pib", "desmatamento_hectare"]].corr(method="pearson")

        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)

        # Save pdf
        path_save = os.path.join(THIS_PATH, "dados", "task_02", "correlation_matrix.pdf")
        plt.title("Matriz de Correlação")
        plt.savefig(path_save, format='pdf')

        print(f"PDF de correlação salvo em: {path_save}")

    # A fom task 2
    dataframe_pib_population = a()

    # B fom task 2
    gframe_deforestation = b()

    # C fom task 2
    c(gframe_deforestation)

    # D fom task 2
    d(dataframe_pib_population, gframe_deforestation)

def task_03():
    """
    - Faça 5 visualizações que possam ser úteis para o gestor público tomar decisões
    sobre onde alocar recursos para fiscalização, elencando os municípios/biomas
    que mais necessitam de atenção. As visualizações podem ser feitas com qualquer
    biblioteca de visualização de dados que você preferir (matplotlib, seaborn, plotly, bokeh, folium, etc)
    e podem ser estáticas ou interativas. Seja criativo e tente fazer visualizações que sejam claras,
    esteticamente agradáveis (PS: Pense que o gestor público não é um cientista de dados e que não tem
    conhecimento de programação ou de ciência de dados e vai apresentar os resultados que você plotar
    neste notebook para o governador do estado alocar mais recursos no combate ao desmatamento ilegal).


    Observações:
    - Como dependia dos dados unificados, salvei um csv na task anterior para conseguir
    ler sem precisar roda-la novamente
    - Salvei os dados em PDF e html, pois assim o gestor não precisará mostrar os códigos e sim documentos.
    """
    # Read csv
    path_date = os.path.join(THIS_PATH, "dados", "desmatamentoDadosUnificados.csv")
    df = pd.read_csv(path_date)

    # Create folder to save plots
    path_save = os.path.join(THIS_PATH, "dados", "task_03")
    os.makedirs(path_save, exist_ok=True)

    # Convert area from km² to hectares
    df["area_ha"] = df["area_km2"] * 100

    # --- 1. Top 10 municipalities (NuFis) with the highest deforested area ---
    top_municipios = df.groupby("NuFis")["area_ha"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(x=top_municipios.values, y=top_municipios.index, palette="Reds_r")
    plt.title("Top 10 Municípios com Maior Área Desmatada (ha)")
    plt.xlabel("Área Desmatada (ha)")
    plt.ylabel("Município")
    plt.tight_layout()
    plt.savefig(os.path.join(path_save, "top_10_municipios.pdf"))
    plt.close()

    # --- 2. Deforested area by biome ---
    bioma_sum = df.groupby("Bioma")["area_ha"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8,6))
    sns.barplot(x=bioma_sum.index, y=bioma_sum.values, palette="Greens_r")
    plt.title("Área Desmatada por Bioma (ha)")
    plt.xlabel("Bioma")
    plt.ylabel("Área Desmatada (ha)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(path_save, "area_por_bioma.pdf"))
    plt.close()

    # --- 3. Monthly deforestation ---
    months = ["agosto", "setembro"]
    # Group by month
    mensal = df.groupby("mes")["area_ha"].sum().reset_index()

    # Ensure all months exist
    mensal = mensal.set_index("mes").reindex(months, fill_value=0).reset_index()
    # Plot
    plt.figure(figsize=(8,6))
    plt.plot(mensal["mes"], mensal["area_ha"], marker='o', color='orange')
    plt.title("Monthly Deforestation (ha)")
    plt.xlabel("Month")
    plt.ylabel("Deforested Area (ha)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(path_save, "desmatamento_mensal.pdf"))
    plt.close()

    # --- 4. Heatmap municipality × biome ---
    pivot = df.pivot_table(index="NuFis", columns="Bioma", values="area_ha", aggfunc="sum").fillna(0)
    plt.figure(figsize=(12,8))
    sns.heatmap(pivot, cmap="Reds", linewidths=.5)
    plt.title("Desmatamento por Município e Bioma (ha)")
    plt.xlabel("Bioma")
    plt.ylabel("Município")
    plt.tight_layout()
    plt.savefig(os.path.join(path_save, "heatmap_municipio_bioma.pdf"))
    plt.close()

    # --- 5. Proportion of deforested area per municipality within each biome ---
    # Group by Biome and Municipality
    prop_df = df.groupby(["Bioma", "NuFis"])["area_ha"].sum().reset_index()

    # Pivot to have municipalities as columns for stacked bar
    pivot_prop = prop_df.pivot(index="Bioma", columns="NuFis", values="area_ha").fillna(0)

    # Normalize to get proportions
    pivot_prop_norm = pivot_prop.div(pivot_prop.sum(axis=1), axis=0)

    # Plot stacked bar chart
    pivot_prop_norm.plot(kind='bar', stacked=True, figsize=(12,6), colormap='tab20')
    plt.title("Proportion of Deforested Area per Municipality within each Biome")
    plt.xlabel("Biome")
    plt.ylabel("Proportion of Area")
    plt.legend(title="Municipality", bbox_to_anchor=(1.05,1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(path_save, "desmatamento_por_municipio_bioma.pdf"))
    plt.close()

    print("Visualizações geradas e salvas em:", path_save)

if __name__ == '__main__':
    #Tasks
    task_01()
    task_02()
    task_03()


    
