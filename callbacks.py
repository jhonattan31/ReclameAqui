# callbacks.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import geopandas as gpd
from dash.dependencies import Input, Output

# Função para gerar a WordCloud dinamicamente
def gerar_imagem_wordcloud(texto_filtrado):
    from wordcloud import WordCloud
    from nltk.corpus import stopwords
    import io
    import base64

    stopwords_portugues = stopwords.words('portuguese')
    novas_stopwords = [
        "produto", "empresa", "comprei", "loja", "não", "pra", "tive", "minha", 
        "dia", "dias", "entrega", "reclame", "aqui", "problema", "já", "pois", 
        "outro", "outra", "Nagem", "fiz", "foi", "disse", "ainda", "ter"
    ]
    stopwords_portugues.extend(novas_stopwords)

    if not texto_filtrado or texto_filtrado.isspace():
        return "" 

    wordcloud = WordCloud(
        width=800, height=350, background_color='white',
        stopwords=stopwords_portugues, colormap='viridis', max_words=100
    ).generate(texto_filtrado)

    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='png')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    return f'data:image/png;base64,{img_base64}'


def register_callbacks(app, df):
    """
    Registra todos os callbacks da aplicação.
    """
    
    @app.callback(
        Output('dados-filtrados-store', 'data'),
        [Input('filtro-estado', 'value'),
         Input('filtro-status', 'value'),
         Input('filtro-tamanho-texto', 'value')]
    )
    def filtrar_e_armazenar_dados(estados, status, faixa_texto):
        dff = df.copy()
        if estados:
            dff = dff[dff['ESTADO'].isin(estados)]
        if status:
            dff = dff[dff['STATUS'].isin(status)]
        if faixa_texto:
            dff = dff[dff['TAMANHO_TEXTO'].between(faixa_texto[0], faixa_texto[1])]
        return dff.to_dict('records')

    @app.callback(Output('grafico-serie-temporal', 'figure'), Input('dados-filtrados-store', 'data'))
    def atualizar_serie_temporal(dados):
        if not dados: return go.Figure().update_layout(title_text="Sem dados para exibir.", template="plotly_white")
        dff = pd.DataFrame(dados)
        dff['TEMPO'] = pd.to_datetime(dff['TEMPO'])
        reclamacoes = dff.set_index('TEMPO').resample('M').size().reset_index(name='CONTAGEM')
        fig = px.line(reclamacoes, x='TEMPO', y='CONTAGEM', title='Volume de Reclamações ao Longo do Tempo')
        fig.update_layout(margin=dict(l=40, r=20, t=40, b=20), height=300, template="plotly_white")
        return fig

    @app.callback(Output('grafico-status', 'figure'), Input('dados-filtrados-store', 'data'))
    def atualizar_grafico_status(dados):
        if not dados: return go.Figure().update_layout(title_text="Sem dados para exibir.", template="plotly_white")
        dff = pd.DataFrame(dados)
        counts = dff['STATUS'].value_counts().reset_index()
        fig = px.pie(counts, names='STATUS', values='count', title='Distribuição por Status', hole=.3)
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300, template="plotly_white")
        return fig

    @app.callback(Output('grafico-estados', 'figure'), Input('dados-filtrados-store', 'data'))
    def atualizar_grafico_estados(dados):
        if not dados: return go.Figure().update_layout(title_text="Sem dados para exibir.", template="plotly_white")
        dff = pd.DataFrame(dados)
        counts = dff['ESTADO'].value_counts().reset_index()
        fig = px.bar(counts, x='ESTADO', y='count', title='Volume de Reclamações por Estado')
        fig.update_layout(margin=dict(l=40, r=20, t=40, b=20), height=300, template="plotly_white")
        return fig
        
    @app.callback(Output('grafico-tamanho-texto', 'figure'), Input('dados-filtrados-store', 'data'))
    def atualizar_histograma_texto(dados):
        if not dados: return go.Figure().update_layout(title_text="Sem dados para exibir.", template="plotly_white")
        dff = pd.DataFrame(dados)
        fig = px.histogram(dff, x='TAMANHO_TEXTO', nbins=50, title='Distribuição do Tamanho das Reclamações')
        fig.update_layout(margin=dict(l=40, r=20, t=40, b=20), height=300, template="plotly_white")
        return fig
    
    @app.callback(Output('imagem-wordcloud', 'src'), Input('dados-filtrados-store', 'data'))
    def atualizar_wordcloud(dados):
        if not dados: return ""
        dff = pd.DataFrame(dados)
        texto_filtrado = " ".join(reclamacao for reclamacao in dff.DESCRICAO.astype(str))
        return gerar_imagem_wordcloud(texto_filtrado)

    @app.callback(
        Output('mapa-reclamacoes', 'figure'),
        [Input('dados-filtrados-store', 'data'),
         Input('filtro-ano-mapa', 'value')]
    )
    def atualizar_mapa(dados_filtrados, ano_selecionado):
        if not dados_filtrados:
            return go.Figure().update_layout(title_text="Selecione filtros para ver o mapa.", template="plotly_white")

        dff = pd.DataFrame(dados_filtrados)
        dff_ano = dff[dff['ANO'] == ano_selecionado]

        if dff_ano.empty:
            return go.Figure().update_layout(title_text=f"Nenhum dado para o ano de {ano_selecionado}.", template="plotly_white")

        reclamacoes_por_estado = dff_ano.groupby('ESTADO').size().reset_index(name='CONTAGEM')
        
        try:
            mapa_base_ibge = gpd.read_file('mapa_data/BR_UF_2022.shp')
        except Exception as e:
            return go.Figure().update_layout(title_text=f"Erro ao carregar mapa: {e}", template="plotly_white")

        coluna_sigla_ibge = 'SIGLA' if 'SIGLA' in mapa_base_ibge.columns else 'SIGLA_UF'
        
        gdf_mapa = mapa_base_ibge.merge(reclamacoes_por_estado, left_on=coluna_sigla_ibge, right_on='ESTADO', how='left')
        gdf_mapa['CONTAGEM'] = gdf_mapa['CONTAGEM'].fillna(0)

        fig = px.choropleth_mapbox(
            gdf_mapa,
            geojson=gdf_mapa.geometry,
            locations=gdf_mapa.index,
            color='CONTAGEM',
            color_continuous_scale="reds",
            mapbox_style="carto-positron",
            zoom=3.2, center={"lat": -15.788497, "lon": -47.879873},
            opacity=0.6,
            hover_name='NM_UF',
            hover_data={'CONTAGEM': True},
            labels={'CONTAGEM': 'Nº de Reclamações'}
        )
        fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
        return fig