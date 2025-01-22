import simpy
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Classe Network ---
class Network:
    """Modelo simples de uma rede óptica."""
    def __init__(self):
        self.graph = nx.Graph()
        self._create_network()
    
    def _create_network(self):
        # Exemplo de uma rede com 5 nós e 6 enlaces
        self.graph.add_edges_from([
            (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5)
        ])
        for u, v in self.graph.edges:
            self.graph[u][v]['slots'] = [True] * 10  # 10 slots disponíveis por enlace

    def allocate_slots(self, path, num_slots):
        """Aloca slots para um caminho."""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            slots = self.graph[u][v]['slots']
            # Exemplo simplificado: usa os primeiros slots disponíveis
            allocated = [i for i, slot in enumerate(slots) if slot][:num_slots]
            if len(allocated) == num_slots:
                for s in allocated:
                    slots[s] = False
                return allocated
        return None

    def release_slots(self, path, slots):
        """Libera slots de um caminho."""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            for s in slots:
                self.graph[u][v]['slots'][s] = True

# --- Classe PacketGenerator ---
class PacketGenerator:
    def __init__(self, env, network, logs, load=0.5):
        self.env = env
        self.network = network
        self.logs = logs  # Lista para armazenar logs
        self.load = load
        self.action = env.process(self.run())

    def log(self, message):
        """Registra uma mensagem de log."""
        timestamp = f"[{self.env.now:.2f}]"
        self.logs.append(f"{timestamp} {message}")

    def run(self):
        while True:
            yield self.env.timeout(np.random.exponential(1 / self.load))
            src, dst = np.random.choice(list(self.network.graph.nodes), 2, replace=False)
            path = nx.shortest_path(self.network.graph, src, dst)
            slots = self.network.allocate_slots(path, num_slots=2)  # 2 slots por pacote
            if slots:
                self.log(f"Pacote enviado: {src} -> {dst}, slots: {slots}")
                yield self.env.timeout(5)  # Duração do pacote
                self.network.release_slots(path, slots)
                self.log(f"Pacote finalizado: {src} -> {dst}, slots liberados.")
            else:
                self.log(f"Pacote perdido: {src} -> {dst} (recursos insuficientes)")

# --- Simulação ---
def run_simulation(duration):
    env = simpy.Environment()
    network = Network()
    logs = []  # Lista para armazenar os logs da simulação
    PacketGenerator(env, network, logs, load=0.7)
    env.run(until=duration)
    return network, logs

# --- Interface com Dash ---
app = Dash(__name__)
app.title = "Desenvolvimento e Teste de Simulador de Redes Ópticas Elásticas com Python"

# Layout
app.layout = html.Div([
    html.Link(href='https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap', rel='stylesheet'),
    html.Div(style={'fontFamily': 'Roboto, sans-serif', 'backgroundColor': '#0e1012', 'color': '#ffffff', 'padding': '100px', 'padding': '20px'}, children=[
        html.Img(src='https://unicv.edu.cv/images/logo_unicv2021.png', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '150px', 'height': 'auto'}),
        html.H1("Simulador de Redes Ópticas Elásticas", style={'textAlign': 'center', 'color': '#808184'}),
        html.P("by Simao Moreno", style={'textAlign': 'center', 'color': '#808184'}),
        
        html.Div([
            html.Label("Duração da Simulação:", style={'color': '#ffffff'}),
            dcc.Input(id='duration-input', type='number', placeholder='Insira a duração', style={'marginRight': '10px'}),
            html.Button("Rodar Simulação", id='run-simulation-btn', n_clicks=0, style={'backgroundColor': '#808184', 'color': '#ffffff'}),
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.H3("Logs da Simulação", style={'color': '#808184'}),
                dcc.Textarea(
                    id='log-output',
                    style={'width': '100%', 'height': '400px', 'backgroundColor': '#333333', 'color': '#ffffff'},
                    readOnly=True
                )
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

            html.Div([
                html.H3("Gráficos da Simulação", style={'color': '#808184'}),
                dcc.Graph(id='simulation-graph')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.H3("Tabela de Slots por Enlace", style={'color': '#808184'}),
                dcc.Graph(id='slots-table')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

            html.Div([
                html.H3("Tabela de Transmissores e Receptores por Nó", style={'color': '#808184'}),
                dcc.Graph(id='txrx-table')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        ], style={'marginBottom': '20px', 'display': 'flex', 'justifyContent': 'space-between'}),

        html.Div(id='output', style={'marginTop': '20px', 'fontSize': '16px', 'color': '#ffffff'}),
    ])
])

# Callback para rodar a simulação
@app.callback(
    [Output('output', 'children'), Output('log-output', 'value'), Output('simulation-graph', 'figure'), Output('slots-table', 'figure'), Output('txrx-table', 'figure')],
    Input('run-simulation-btn', 'n_clicks'),
    State('duration-input', 'value')
)
def update_simulation(n_clicks, duration):
    if n_clicks > 0 and duration:
        try:
            network, logs = run_simulation(duration)
            # Visualização do uso de slots
            edges = list(network.graph.edges(data=True))
            slots_usage = [
                len([s for s in edge[2]['slots'] if not s]) for edge in edges
            ]
            fig = go.Figure(data=[
                go.Bar(x=[f"{u}-{v}" for u, v, _ in edges], y=slots_usage, name="Uso de Slots")
            ])
            fig.update_layout(title="Uso de Slots nos Enlaces", xaxis_title="Enlaces", yaxis_title="Slots Usados", plot_bgcolor='#0e1012', paper_bgcolor='#0e1012', font=dict(color='#ffffff'))

            # Desenho dos nós e ligações
            pos = nx.spring_layout(network.graph)
            edge_x = []
            edge_y = []
            for edge in network.graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.append(x0)
                edge_x.append(x1)
                edge_x.append(None)
                edge_y.append(y0)
                edge_y.append(y1)
                edge_y.append(None)
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines')

            node_x = []
            node_y = []
            for node in network.graph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    size=10,
                    colorbar=dict(
                        thickness=15,
                        title='Node Connections',
                        xanchor='left',
                        titleside='right'
                    ),
                ),
                text=[str(node) for node in network.graph.nodes()])

            fig_network = go.Figure(data=[edge_trace, node_trace])
            fig_network.update_layout(title="Topologia da Rede", showlegend=False, plot_bgcolor='#0e1012', paper_bgcolor='#0e1012', font=dict(color='#ffffff'))

            # Tabela de slots por enlace
            slots_table = go.Figure(data=[go.Table(
                header=dict(values=['Enlace', 'Slots Usados'], fill_color='#808184', font=dict(color='white')),
                cells=dict(values=[[f"{u}-{v}" for u, v, _ in edges], slots_usage], fill_color='#333333', font=dict(color='white'))
            )])
            slots_table.update_layout(title="Tabela de Slots por Enlace", plot_bgcolor='#0e1012', paper_bgcolor='#0e1012', font=dict(color='#ffffff'))

            # Tabela de transmissores e receptores por nó
            txrx_data = np.zeros((network.graph.number_of_nodes(), 2))
            for node in network.graph.nodes():
                txrx_data[node-1, 0] = 10  # Exemplo: 10 transmissores por nó
                txrx_data[node-1, 1] = 10  # Exemplo: 10 receptores por nó
            txrx_table = go.Figure(data=[go.Table(
                header=dict(values=['Nó', 'Transmissores', 'Receptores'], fill_color='#808184', font=dict(color='white')),
                cells=dict(values=[[node for node in network.graph.nodes()], txrx_data[:, 0], txrx_data[:, 1]], fill_color='#333333', font=dict(color='white'))
            )])
            txrx_table.update_layout(title="Tabela de Transmissores e Receptores por Nó", plot_bgcolor='#0e1012', paper_bgcolor='#0e1012', font=dict(color='#ffffff'))

            return "Simulação concluída.", "\n".join(logs), fig_network, slots_table, txrx_table
        except Exception as e:
            return f"Ocorreu um erro: {str(e)}", "", go.Figure(), go.Figure(), go.Figure()
    return "Insira a duração e clique em 'Rodar Simulação'.", "", go.Figure(), go.Figure(), go.Figure()

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)