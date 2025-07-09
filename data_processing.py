# data_processing.py

import pandas as pd
from wordcloud import WordCloud
from nltk.corpus import stopwords
import io
import base64

FILE_PATH = 'dataset/RECLAMEAQUI_NAGEM.csv'

def load_and_prepare_data():
    """
    Função principal que carrega e processa todos os dados para o dashboard.
    """
    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de dados não encontrado em '{FILE_PATH}'. Verifique o caminho e a pasta.")

    df['TEMPO'] = pd.to_datetime(df['TEMPO'])
    df['ANO'] = df['TEMPO'].dt.year
    df['ESTADO'] = df['LOCAL'].str.split(' - ').str[-1].str.strip().str.upper()
    df['TAMANHO_TEXTO'] = df['DESCRICAO'].astype(str).str.split().str.len()

    stopwords_portugues = stopwords.words('portuguese')
    novas_stopwords = [
        "produto", "empresa", "comprei", "loja", "não", "pra", "tive", "minha", 
        "dia", "dias", "entrega", "reclame", "aqui", "problema", "já", "pois", 
        "outro", "outra", "Nagem", "fiz", "foi", "disse", "ainda", "ter"
    ]
    stopwords_portugues.extend(novas_stopwords)

    texto_completo = " ".join(reclamacao for reclamacao in df.DESCRICAO.astype(str))

    wordcloud = WordCloud(
        width=800, height=350, background_color='white',
        stopwords=stopwords_portugues, colormap='viridis', max_words=100
    ).generate(texto_completo)

    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='png')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    imagem_wordcloud_src = f'data:image/png;base64,{img_base64}'

    lista_estados = sorted(df['ESTADO'].dropna().unique())
    lista_status = sorted(df['STATUS'].dropna().unique())

    return df, imagem_wordcloud_src, lista_estados, lista_status