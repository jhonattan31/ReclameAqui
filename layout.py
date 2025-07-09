# layout.py

from dash import dcc, html

def create_layout(lista_estados, lista_status, df):
    """
    Cria e retorna o layout completo do dashboard do Reclame Aqui.
    """
    min_texto = int(df['TAMANHO_TEXTO'].min())
    max_texto = int(df['TAMANHO_TEXTO'].max())

    layout = html.Div(className='app-container', children=[
        
        html.H1("Dashboard de Análise de Reclamações - Nagem", className='main-title'),

        html.Div(className='header-section', children=[
            html.P("Utilize os filtros abaixo para explorar os dados de reclamações da Nagem.", className='intro-text')
        ]),
        
        html.Div(className='controls-container', children=[
            html.Div(className='control-group', children=[
                html.Label("Filtrar por Estado:", className='control-label'),
                dcc.Dropdown(
                    id='filtro-estado',
                    options=[{'label': i, 'value': i} for i in lista_estados],
                    placeholder="Todos os Estados",
                    multi=True
                )
            ]),
            html.Div(className='control-group', children=[
                html.Label("Filtrar por Status:", className='control-label'),
                dcc.Dropdown(
                    id='filtro-status',
                    options=[{'label': i, 'value': i} for i in lista_status],
                    placeholder="Todos os Status",
                    multi=True
                )
            ]),
            html.Div(className='control-group', style={'width': '100%'}, children=[
                html.Label("Filtrar por Tamanho do Texto (palavras):", className='control-label'),
                dcc.RangeSlider(
                    id='filtro-tamanho-texto',
                    min=min_texto,
                    max=max_texto,
                    value=[min_texto, max_texto],
                    marks={i: str(i) for i in range(min_texto, max_texto + 1, 200)},
                    step=10,
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ]),
        ]),

        html.Div(className='main-content', children=[
            html.Div(className='chart-card', children=[
                html.H3("Reclamações ao Longo do Tempo", className='chart-title'),
                dcc.Graph(id='grafico-serie-temporal', style={'height': '300px'})
            ]),
            html.Div(className='chart-card', children=[
                html.H3("Distribuição por Status", className='chart-title'),
                dcc.Graph(id='grafico-status', style={'height': '300px'})
            ]),
            html.Div(className='chart-card', children=[
                html.H3("Reclamações por Estado", className='chart-title'),
                dcc.Graph(id='grafico-estados', style={'height': '300px'})
            ]),
            html.Div(className='chart-card', children=[
                html.H3("Distribuição do Tamanho do Texto", className='chart-title'),
                dcc.Graph(id='grafico-tamanho-texto', style={'height': '300px'})
            ]),
            html.Div(className='chart-card full-width', children=[
                html.H3("Termos Mais Frequentes nas Descrições", className='chart-title'),
                html.Img(id='imagem-wordcloud', style={'width': '100%', 'height': 'auto', 'maxHeight': '400px'})
            ]),
            html.Div(className='chart-card full-width', children=[
                html.H3("Mapa de Reclamações por Estado", className='chart-title'),
                html.Div(className='control-group', style={'maxWidth': '300px', 'marginBottom': '15px'}, children=[
                    html.Label("Selecione o Ano:", className='control-label'),
                    dcc.Dropdown(
                        id='filtro-ano-mapa',
                        options=[{'label': str(ano), 'value': ano} for ano in sorted(df['ANO'].unique())],
                        value=df['ANO'].max()
                    ),
                ]),
                dcc.Graph(id='mapa-reclamacoes', style={'height': '65vh'})
            ])
        ]),

        dcc.Store(id='dados-filtrados-store')
    ])
    
    return layout