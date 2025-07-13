#app.py
from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
from data_processing import FILE_PATH_Saida
import pandas as pd

# Leitura do dataset preprocessado
df = pd.read_csv(FILE_PATH_Saida, parse_dates=['DATA'])
lista_estados = sorted(df['ESTADO'].dropna().unique())
lista_status = sorted(df['STATUS'].dropna().unique())

# Inicializa o app
app = Dash(__name__, assets_folder='assets')
app.title = "Dashboard Reclame Aqui - Nagem"

# Define o layout
app.layout = create_layout(lista_estados, lista_status, df)

# Registra os callbacks
register_callbacks(app, df)

# 👇 ESSENCIAL para o deploy funcionar com gunicorn
server = app.server

# Apenas para rodar localmente
if __name__ == '__main__':
    app.run(debug=True)
