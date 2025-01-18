import simpy
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import networkx as nx
import numpy as np
import plotly.graph_objects as go

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
app.title = "Simulador de Redes Ópticas Elásticas"

# Layout
app.layout = html.Div([
    html.H1("Simulador de Redes Ópticas Elásticas", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Duração da Simulação:"),
        dcc.Input(id='duration-input', type='number', placeholder='Insira a duração', style={'marginRight': '10px'}),
        html.Button("Rodar Simulação", id='run-simulation-btn', n_clicks=0),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.H3("Logs da Simulação"),
        dcc.Textarea(
            id='log-output',
            style={'width': '100%', 'height': '200px'},
            readOnly=True
        )
    ], style={'marginBottom': '20px'}),

    html.Div(id='output', style={'marginTop': '20px', 'fontSize': '16px'}),
])

# Callback para rodar a simulação
@app.callback(
    [Output('output', 'children'), Output('log-output', 'value')],
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
            fig.update_layout(title="Uso de Slots nos Enlaces", xaxis_title="Enlaces", yaxis_title="Slots Usados")
            return dcc.Graph(figure=fig), "\n".join(logs)
        except Exception as e:
            return f"Ocorreu um erro: {str(e)}", ""
    return "Insira a duração e clique em 'Rodar Simulação'.", ""

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
