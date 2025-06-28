import pandas as pd
import numpy as np
import geopandas
import unicodedata # Para remoção de acentos
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATH_DESCRITORES = os.path.join(BASE_DIR, '..', '..', 'datasets', 'DESCRITORESMATH.csv')
FILE_PATH_SHP = os.path.join(BASE_DIR, '..', '..', 'datasets', 'Limites_municipais_Ceara2021', 'Limites_municipais_IPECE_2021_utm_sirgas_2000.shp')


# --- Dicionário de Descritores (ATUALIZADO COM BASE NO PDF) ---
DESCRITORES_MAP = {
    'D16': 'D16: Relações Fracionárias e Decimais',
    'D19': 'D19: Juros Simples',
    'D20': 'D20: Juros Compostos',
    'D24': 'D24: Fatorar e Simplificar Expressões Algébricas',
    'D28': 'D28: Função Polinomial 1º Grau (Algébrica/Gráfica)',
    'D40': 'D40: Raízes de Polinômios e Fatores 1º Grau',
    'D42': 'D42: Probabilidade de um Evento',
    'D49': 'D49: Semelhança de Figuras Planas',
    'D50': 'D50: Teorema de Pitágoras e Relações Métricas',
    'D51': 'D51: Propriedades dos Polígonos',
    'D52': 'D52: Planificações de Poliedros/Corpos Redondos',
    'D53': 'D53: Razões Trigonométricas no Triângulo Retângulo',
    'D54': 'D54: Área de Triângulo por Coordenadas',
    'D55': 'D55: Equação da Reta (2 Pontos/Ponto-Inclinação)',
    'D56': 'D56: Equações de Circunferências',
    'D57': 'D57: Localização de Pontos no Plano Cartesiano',
    'D58': 'D58: Coeficientes da Equação de uma Reta (Geometria)',
    'D64': 'D64: Unidades de Medida (Capacidade e Volume)',
    'D65': 'D65: Perímetro de Figuras Planas',
    'D67': 'D67: Área de Figuras Planas',
    'D71': 'D71: Área da Superfície Total de Sólidos',
    'D72': 'D72: Volume de Sólidos',
    'D76': 'D76: Informações em Listas/Tabelas e Gráficos',
    'D78': 'D78: Medidas de Tendência Central',
}
# --- Mapas e Ordens Padrão ---
MAP_PADRAO_NUMERICO = {'Muito Crítico': 1, 'Crítico': 2, 'Intermediário': 3, 'Adequado': 4}
ORDEM_PADRAO_CATEGORIAS = ['Muito Crítico', 'Crítico', 'Intermediário', 'Adequado']
CORES_PARA_PADRAO = {
    'Muito Crítico': '#DC3545',
    'Crítico': '#FD7E14',
    'Intermediário': '#FFC107',
    'Adequado': '#28A745'
}

def padronizar_nome_municipio(nome):
    if pd.isna(nome): return nome
    nome = str(nome).upper().strip()
    nome = unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('utf-8')
    return nome

def load_and_process_df(path=FILE_PATH_DESCRITORES):
    df = pd.read_csv(path)
    df = df.rename(columns={k: v for k, v in DESCRITORES_MAP.items() if k in df.columns})
    df['Município_Padronizado'] = df['Município'].apply(padronizar_nome_municipio)
    df['_Padrao_Temp_Numerico'] = df['Indicação do Padrão de Desempenho'].map(MAP_PADRAO_NUMERICO)
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    return df

def load_and_process_gdf(path=FILE_PATH_SHP):
    gdf = geopandas.read_file(path)
    gdf['Município'] = gdf['Municipio'].apply(padronizar_nome_municipio)
    gdf['Município'] = gdf['Município'].replace({'DEP. IRAPUAN PINHEIRO': 'DEPUTADO IRAPUAN PINHEIRO'})
    return gdf

def get_moda_padrao(df):
    return (
        df.groupby('Município')['Indicação do Padrão de Desempenho']
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index(name='Moda_Padrao_Desempenho')
    )

def get_all_data():
    df = load_and_process_df()
    gdf = load_and_process_gdf()
    if df is None or gdf is None:
        raise RuntimeError("Erro ao carregar os dados")

    moda_df = get_moda_padrao(df)
    gdf_moda = gdf.merge(moda_df, on='Município', how='left')
    gdf_moda['Moda_Padrao_Desempenho'] = pd.Categorical(
        gdf_moda['Moda_Padrao_Desempenho'],
        categories=ORDEM_PADRAO_CATEGORIAS,
        ordered=True
    ).add_categories('Dados Ausentes').fillna('Dados Ausentes')

    lista_descritores = sorted([d for d in DESCRITORES_MAP.values() if d in df.columns])
    lista_municipios = sorted(df['Município'].unique())
    lista_municipios_dropdown = [{'label': m, 'value': m} for m in lista_municipios]
    lista_municipios_dropdown.insert(0, {'label': 'Todos', 'value': 'Todos'})

    return df, gdf, gdf_moda, lista_descritores, lista_municipios, lista_municipios_dropdown
