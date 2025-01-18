import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# Inicializar a aplicação Dash
app = dash.Dash(__name__)

# Layout básico da aplicação
app.layout = html.Div([
    html.H1("Simulador de Redes Ópticas Elásticas", style={'textAlign': 'center'}),
    
    # Botão para acionar uma simulação
    html.Button("Rodar Simulação", id='run-simulation-btn', n_clicks=0),
    
    # Área para mostrar os resultados
    html.Div(id='output', style={'marginTop': '20px', 'fontSize': '20px'}),
])

# Callback para atualizar o resultado
@app.callback(
    Output('output', 'children'),
    Input('run-simulation-btn', 'n_clicks')  # Monitorar cliques no botão
)
def update_output(n_clicks):
    if n_clicks > 0:
        # Aqui você colocaria o resultado do simulador, por exemplo:
        taxa_bloqueio = 0.05  # Simulação fictícia
        return f"Simulação concluída! Taxa de bloqueio = {taxa_bloqueio:.2f}"
    return "Clique no botão para rodar a simulação."

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
