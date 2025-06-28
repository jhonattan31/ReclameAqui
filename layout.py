# layout.py

from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from matplotlib.colors import ListedColormap

def create_initial_scatter_plot():
    return px.scatter(title="Selecione Município e Descritores para o Scatter Plot")

def create_initial_municipio_map():
    return px.choropleth_mapbox(
        mapbox_style="carto-positron",
        zoom=6.5,
        center={"lat": -5.0, "lon": -39.5},
        title="Carregando Mapa de Desempenho por Município..."
    )

def create_initial_histogram():
    empty_df = pd.DataFrame({'dummy': []})
    fig = px.histogram(empty_df, x='dummy', title="Selecione um Descritor e Município para o Histograma")
    return fig

def create_initial_correlation_matrix():
    fig = go.Figure(go.Heatmap(z=[[0,0],[0,0]], x=['Desc. A', 'Desc. B'], y=['Desc. A', 'Desc. B'], colorscale='Viridis'))
    fig.update_layout(title_text="Carregando Matriz de Correlação...")
    return fig

def get_layout(
    gdf_moda_final, CORES_PARA_PADRAO, ORDEM_PADRAO_CATEGORIAS,
    LISTA_DESCRITORES, LISTA_MUNICIPIOS_DROPDOWN_OPTIONS, LISTA_ESTATISTICAS_MAPA
):
    return html.Div(className='app-container', children=[
        html.H1("Dashboard de Desempenho Educacional: Descritores SAEB - Ceará"),
        html.Div([
            html.Label("Selecione o Município:"),
            dcc.Dropdown(id='dropdown-municipio-global', options=LISTA_MUNICIPIOS_DROPDOWN_OPTIONS, value='Todos')
        ]),
        html.Div([
            html.H2("1. Análise de Relação entre Descritores"),
            dcc.Dropdown(id='scatter-descritor-x', options=[{'label': d, 'value': d} for d in LISTA_DESCRITORES], value=LISTA_DESCRITORES[0]),
            dcc.Dropdown(id='scatter-descritor-y', options=[{'label': d, 'value': d} for d in LISTA_DESCRITORES], value=LISTA_DESCRITORES[1]),
            dcc.Graph(id='scatter-plot-descritores', figure=create_initial_scatter_plot()),
        ]),
        html.Div([
            html.H2("2. Mapa de Desempenho por Município"),
            dcc.Dropdown(id='map-descritor', options=[{'label': d, 'value': d} for d in LISTA_DESCRITORES], value=LISTA_DESCRITORES[0]),
            dcc.Dropdown(id='map-estatistica', options=[{'label': e, 'value': e} for e in LISTA_ESTATISTICAS_MAPA], value='Média'),
            dcc.Graph(id='municipio-map', figure=create_initial_municipio_map()),
        ]),
        html.Div([
            html.H2("3. Histograma"),
            dcc.Dropdown(id='histogram-descritor', options=[{'label': d, 'value': d} for d in LISTA_DESCRITORES], value=LISTA_DESCRITORES[0]),
            dcc.Graph(id='histogram-plot', figure=create_initial_histogram())
        ]),
        html.Div([
            html.H2("4. Matriz de Correlação"),
            dcc.Graph(id='correlation-matrix-plot', figure=create_initial_correlation_matrix())
        ]),
        dcc.Store(id='filtered-data-store')
    ])
