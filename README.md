# Teste de conhecimento AgronomiQ

## Author
João Paulo Cardoso do Carmo  
Date: 2025-08-30

## Description
Este projeto realiza uma análise de dados de desmatamento em Minas Gerais, integrando informações geoespaciais, população e PIB dos municípios.  
O código possui tarefas que incluem download e processamento de dados geográficos, análise exploratória e geração de visualizações úteis para gestores públicos.

## Requirements
Para rodar o projeto, é necessário ter instalado:

- Python 3.10.13
- Bibliotecas:
  - `geopandas`
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `branca`
  - `requests`
  
Você pode instalar todas as dependências com:

```bash
pip install -r requirements.txt
````

---

## Tasks

### Task 01

* Download dos dados municipais de Minas Gerais.
* Transformação de dados geoespaciais.
* Cálculo de área de cada município (km²).
* Geração de arquivo GeoJSON (`municipios-mg.geojson`).

### Task 02

* Obtenção de dados de população e PIB por município (`populacao-pib-municipios-mg.csv`).
* Consolidação de focos de desmatamento em um único GeoJSON (`focos-desmatamento-mg.geojson`).
* Análise exploratória de:

  * Área desmatada por mês (agosto e setembro 2022) em hectares.
  * Área total desmatada por bioma e município.
  * Correlação entre população, PIB e área desmatada.

### Task 03

* Geração de 5 visualizações para gestores públicos:

  1. Top 10 municípios com maior área desmatada.
  2. Área desmatada por bioma.
  3. Desmatamento mensal.
  4. Heatmap de município × bioma.
  5. Proporção de área desmatada por município dentro de cada bioma.
* Visualizações salvas em PDF.

---

## How to Run

No terminal, execute:

```bash
python agronomiq.py
```
---

## Notes

* Foi feito em arquivo .py por ser mais robusto e pronto para automações e processos, entretanto, também foi adicionado os códigos ipynb em "./tasks".
* GeoJSONs não foram salvos em UTM, pois isso pode gerar problemas de compatibilidade.
* Task 03 depende dos dados consolidados na Task 02.
* As análises e visualizações foram pensadas para gestores públicos, não sendo necessário conhecimento técnico avançado.

