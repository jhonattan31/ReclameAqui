from dash import Dash
from layout import get_layout  # Atualizado para a função get_layout
from callbacks import register_callbacks
from data_processing import get_all_data

# Carrega todos os dados de uma vez
df, gdf_ceara, gdf_moda_final, LISTA_DESCRITORES, LISTA_MUNICIPIOS, LISTA_MUNICIPIOS_DROPDOWN_OPTIONS = get_all_data()

# Defina uma lista estática das estatísticas para dropdown no layout
LISTA_ESTATISTICAS_MAPA = ['Média', 'Mediana', 'Maior Valor', 'Menor Valor']

# Define cores e categorias usados no layout
from data_processing import CORES_PARA_PADRAO, ORDEM_PADRAO_CATEGORIAS

# Inicializa o app Dash
app = Dash(__name__)
app.title = "Dashboard SAEB - Ceará"

# Associa o layout ao app, passando os dados necessários
app.layout = get_layout(
    gdf_moda_final=gdf_moda_final,
    CORES_PARA_PADRAO=CORES_PARA_PADRAO,
    ORDEM_PADRAO_CATEGORIAS=ORDEM_PADRAO_CATEGORIAS,
    LISTA_DESCRITORES=LISTA_DESCRITORES,
    LISTA_MUNICIPIOS_DROPDOWN_OPTIONS=LISTA_MUNICIPIOS_DROPDOWN_OPTIONS,
    LISTA_ESTATISTICAS_MAPA=LISTA_ESTATISTICAS_MAPA
)

# Registra os callbacks, passando também os dados para uso interno
register_callbacks(
    app=app,
    df=df,
    gdf_ceara=gdf_ceara,
    LISTA_DESCRITORES=LISTA_DESCRITORES,
    ORDEM_PADRAO_CATEGORIAS=ORDEM_PADRAO_CATEGORIAS,
    CORES_PARA_PADRAO=CORES_PARA_PADRAO
)


# Executa o servidor
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
