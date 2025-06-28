import unidecode
import json
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Paleta para Histograma e Scatter
ORDEM_E_CORES_HISTOGRAMA = {
    'Muito Crítico': '#DC3545',
    'Crítico': '#FD7E14',
    'Intermediário': '#FFC107',
    'Adequado': '#28A745'
}

# Registra todos os callbacks no app
def register_callbacks(app, df: pd.DataFrame, gdf_ceara, 
                       LISTA_DESCRITORES, ORDEM_PADRAO_CATEGORIAS, CORES_PARA_PADRAO):

    # --- Callback: Armazena dados filtrados (usado nos demais gráficos) ---
    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('dropdown-municipio-global', 'value')
    )
    def store_filtered_data(selected_municipio):
        if selected_municipio == 'Todos':
            dff = df.copy()
        else:
            dff = df[df['Município'] == selected_municipio].copy()
        return dff.to_dict('records')

    # --- Callback: Scatter Plot entre dois descritores ---
    @app.callback(
        Output('scatter-plot-descritores', 'figure'),
        Input('filtered-data-store', 'data'),
        Input('scatter-descritor-x', 'value'),
        Input('scatter-descritor-y', 'value')
    )
    def update_scatter_plot(stored_data, descritor_x, descritor_y):
        dff = pd.DataFrame(stored_data)

        if dff.empty:
            return px.scatter(title="Dados não disponíveis para esta seleção.")

        fig = px.scatter(
            dff,
            x=descritor_x, y=descritor_y,
            color='Indicação do Padrão de Desempenho',
            color_discrete_map=ORDEM_E_CORES_HISTOGRAMA,
            category_orders={"Indicação do Padrão de Desempenho": ORDEM_PADRAO_CATEGORIAS},
            hover_name="Município",
            hover_data={'Escola': True, descritor_x: ':.2f', descritor_y: ':.2f'},
            title=f"Desempenho: {descritor_x} vs. {descritor_y}"
        )
        fig.update_layout(transition_duration=500)
        return fig

    # --- Callback: Mapa com estatística de um descritor ---
    @app.callback(
        Output('municipio-map', 'figure'),
        Input('map-descritor', 'value'),
        Input('map-estatistica', 'value')
    )
    def update_municipio_map(selected_descritor, selected_estatistica):
        # Normaliza os nomes para garantir matching exato
        def normalize_text(s):
            if pd.isna(s):
                return s
            return unidecode.unidecode(s).upper()

        df['Municipio_norm'] = df['Município'].apply(normalize_text)
        gdf_ceara['Municipio_norm'] = gdf_ceara['Município'].apply(normalize_text)
        
        # Calcula a estatística escolhida
        if selected_estatistica == 'Média':
            stats_df = df.groupby('Municipio_norm')[selected_descritor].mean().reset_index()
        elif selected_estatistica == 'Mediana':
            stats_df = df.groupby('Municipio_norm')[selected_descritor].median().reset_index()
        elif selected_estatistica == 'Maior Valor':
            stats_df = df.groupby('Municipio_norm')[selected_descritor].max().reset_index()
        elif selected_estatistica == 'Menor Valor':
            stats_df = df.groupby('Municipio_norm')[selected_descritor].min().reset_index()
        else:
            stats_df = df.groupby('Municipio_norm')[selected_descritor].mean().reset_index()

        stats_df.rename(columns={selected_descritor: 'Valor_Estatistica'}, inplace=True)
        
        # Merge com GeoDataFrame
        gdf_mapa = gdf_ceara.merge(stats_df, on='Municipio_norm', how='left')

        gdf_mapa_wgs84 = gdf_mapa.to_crs(epsg=4326)

        geojson = json.loads(gdf_mapa_wgs84.to_json())

        # Cria o gráfico
        fig = px.choropleth_mapbox(
            gdf_mapa_wgs84,
            geojson=geojson,
            locations=gdf_mapa_wgs84.index,
            color='Valor_Estatistica',
            color_continuous_scale='RdYlGn',
            mapbox_style='carto-positron',
            zoom=6.5,
            center={"lat": -5.0, "lon": -39.5},
            opacity=0.7,
            labels={'Valor_Estatistica': f'{selected_estatistica} de {selected_descritor}'},
            hover_name='Municipio_norm',
            hover_data={'Valor_Estatistica': ':.2f'}
        )

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig

    # --- Callback: Histograma por descritor ---
    @app.callback(
        Output('histogram-plot', 'figure'),
        Input('filtered-data-store', 'data'),
        Input('histogram-descritor', 'value'),
        Input('dropdown-municipio-global', 'value')
    )
    def update_histogram(stored_data, selected_descritor, selected_municipio):
        dff = pd.DataFrame(stored_data)

        if dff.empty:
            return px.histogram(title=f"Dados não disponíveis para {selected_municipio}.")

        title = f"Distribuição em {selected_descritor}"
        if selected_municipio != 'Todos':
            title += f" em {selected_municipio}"

        fig = px.histogram(
            dff,
            x=selected_descritor,
            color='Indicação do Padrão de Desempenho',
            color_discrete_map=ORDEM_E_CORES_HISTOGRAMA,
            category_orders={"Indicação do Padrão de Desempenho": ORDEM_PADRAO_CATEGORIAS},
            nbins=20,
            labels={'x': 'Pontuação', 'y': 'Frequência'},
            title=title
        )
        fig.update_layout(xaxis_title="Pontuação", yaxis_title="Frequência", transition_duration=500)
        return fig

    # --- Callback: Matriz de Correlação ---
    @app.callback(
        Output('correlation-matrix-plot', 'figure'),
        Input('filtered-data-store', 'data'),
        Input('dropdown-municipio-global', 'value')
    )
    def update_correlation_matrix(stored_data, selected_municipio):
        dff = pd.DataFrame(stored_data)
        descritores_validos = [d for d in LISTA_DESCRITORES if d in dff.columns and pd.api.types.is_numeric_dtype(dff[d])]

        if dff.empty or not descritores_validos:
            fig = go.Figure(go.Heatmap(z=[[0,0],[0,0]], x=['Sem Dados'], y=['Sem Dados'], colorscale='Viridis'))
            fig.update_layout(title_text=f"Dados insuficientes para {selected_municipio}")
            return fig

        corr_matrix = dff[descritores_validos].corr()

        title = "Matriz de Correlação"
        if selected_municipio != 'Todos':
            title += f" para {selected_municipio}"

        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu',
            range_color=[-1, 1],
            labels=dict(color="Correlação"),
            title=title
        )
        fig.update_layout(height=800, width=1000, margin=dict(t=50, b=10, l=10, r=10))
        fig.update_xaxes(side="top")
        return fig
