import geopandas
import unicodedata # Para remoção de acentos
import pandas as pd
import os
import re
import nltk
from nltk.corpus import stopwords

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminhos dos arquivos
FILE_PATH_Entrada = os.path.join(BASE_DIR, 'dataset', 'RECLAMEAQUI_NAGEM.csv')
FILE_PATH_Saida = os.path.join(BASE_DIR, 'dataset', 'RECLAMEAQUI_NAGEM_AJUSTADO.csv')
#FILE_PATH_SHP = os.path.join(BASE_DIR, '..', '..', 'datasets', 'Limites_municipais_Ceara2021', 'Limites_municipais_IPECE_2021_utm_sirgas_2000.shp')



# Baixar recursos do NLTK se necessário
nltk.download('stopwords')


# Leitura do CSV original
df = pd.read_csv(FILE_PATH_Entrada)

# 1. Criar a coluna de data formatada (DATA)
df['DATA'] = pd.to_datetime(
    df['ANO'].astype(str) + '-' +
    df['MES'].astype(str).str.zfill(2) + '-' +
    df['DIA'].astype(str).str.zfill(2),
    errors='coerce'
)

# 2. Separar 'LOCAL' em 'CIDADE' e 'ESTADO'
df[['CIDADE', 'ESTADO']] = df['LOCAL'].str.extract(r'^(.*) - ([A-Z]{2})$')


# 3. Calcular o tamanho do texto da reclamação
df['DESCRICAO'] = df['DESCRICAO'].fillna('')
df['TAMANHO_TEXTO'] = df['DESCRICAO'].str.len()

# 4. Criar faixas de tamanho do texto
bins = [0, 100, 300, 10000]
labels = ['Curto', 'Médio', 'Longo']
df['FAIXA_TEXTO'] = pd.cut(df['TAMANHO_TEXTO'], bins=bins, labels=labels)

# 5. Limpeza e tokenização da descrição com split (sem punkt)
stopwords_pt = set(stopwords.words('portuguese'))

# Define palavras extras para remover
palavras_extras = {'Nagem', 'nagem', 'pois', 'pra', 'ter', 'tudo', 'outra', 'a', 'ao', 'aos', 'as', 'à', 'às', 'ante', 'após', 'até', 'com', 'contra', 'de', 'desde', 'diante', 'em', 'entre', 'para', 'por', 'perante', 'sem', 'sob', 'sobre', 'trás', 'durante', 'mediante', 'conforme', 'salvo', 'exceto', 'segundo', 'rumo', 'via',
'e', 'ou', 'mas', 'porque', 'porquê', 'pois', 'portanto', 'contudo', 'entretanto', 'porém', 'embora', 'já que', 'uma vez que', 'caso', 'ainda que', 'se', 'como', 'quando', 'onde', 'enquanto', 'depois que', 'logo que', 'assim que', 'antes que', 'sou', 'é', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'seja', 'sejam', 'ser', 'estou', 'está', 'estamos', 'estão', 'estava', 'estávamos', 'estavam', 'esteja', 'estejam', 'estar', 'tenho', 'tem', 'temos', 'têm', 'tinha', 'tínhamos', 'tinham', 'tenha', 'tenham', 'ter', 'hei', 'há', 'havemos', 'hão', 'havia', 'houvéramos', 'houveram', 'haja', 'hajam', 'haver', 'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes', 'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'do', 'da', 'dos', 'das', 'no', 'na', 'nos', 'nas', 'neste', 'nesta', 'nesses', 'nessas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa', 'vossos', 'vossas',
'isso', 'isto', 'aquilo', 'que', 'quem', 'qual', 'quais', 'cujo', 'cuja', 'onde', 'como', 'quando', 'quanto', 'por', 'para', 'também', 'muito', 'muitos', 'muita', 'muitas', 'pouco', 'pouca', 'poucos', 'poucas', 'todo', 'toda', 'todos', 'todas', 'algum', 'alguma', 'alguns', 'algumas', 'nenhum', 'nenhuma', 'nunca', 'sempre', 'já', 'ainda',
}

# Une os dois conjuntos
stopwords_pt.update(palavras_extras)

def preprocessar_texto(texto):
    if pd.isna(texto):
        return []
    texto = texto.lower()  # Minúsculas
    texto = re.sub(r'[^a-záéíóúâêîôûãõç ]', '', texto)  # Remove pontuação e números
    tokens = texto.split()  # Tokenização simples por espaços
    tokens_filtrados = [t for t in tokens if t not in stopwords_pt and len(t) > 2]
    return tokens_filtrados

df['DESCRICAO_TOKENIZADA'] = df['DESCRICAO'].apply(preprocessar_texto)

# 6. Reorganizar colunas
colunas_ordenadas = [
    'ID', 'DATA', 'ANO', 'MES', 'DIA', 'DIA_DO_ANO', 'SEMANA_DO_ANO', 'DIA_DA_SEMANA', 'TRIMETRES',
    'CIDADE', 'ESTADO', 'TEMA', 'CATEGORIA', 'STATUS', 'TAMANHO_TEXTO', 'FAIXA_TEXTO',
    'DESCRICAO', 'DESCRICAO_TOKENIZADA', 'CASOS', 'URL'
]
df = df[colunas_ordenadas]

# 7. Exportar para CSV
df.to_csv(FILE_PATH_Saida, index=False, encoding='utf-8-sig')

print("Arquivo pré-processado salvo em:", FILE_PATH_Saida)

