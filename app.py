# app.py

from dash import Dash
from data_processing import load_and_prepare_data
from layout import create_layout
from callbacks import register_callbacks

# Carrega e prepara os dados
print("Carregando e processando os dados...")
df, imagem_wordcloud_src, lista_estados, lista_status = load_and_prepare_data()
print("Dados carregados com sucesso!")

# Inicializa o app
app = Dash(__name__, assets_folder='assets')
app.title = "Dashboard Reclame Aqui - Nagem"

# Define o layout
app.layout = create_layout(lista_estados, lista_status, df)

# Registra os callbacks
# A função em si não precisa de todos os argumentos, mas o app precisa deles para os callbacks
register_callbacks(app, df) 

# Executa o servidor
if __name__ == '__main__':
    app.run(debug=True) # <-- LINHA CORRIGIDA