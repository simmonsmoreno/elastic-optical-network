import networkx as nx
import simpy
import time
from components.light_path_control import Control
from components.light_path_generator import LightPathGenerator
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.tree import Tree
import matplotlib.pyplot as plt

# Constantes
NODES = [1, 2, 3, 4, 5]
EDGES = [
    (1, 2), (2, 1), (1, 4), (4, 1),
    (2, 3), (3, 2), (2, 5), (5, 2),
    (3, 5), (5, 3), (4, 5), (5, 4)
]
ALLOCATION_ALGORITHMS = {"0": "first_fit", "1": "best_gap"}

console = Console()

def create_network():
    """Cria o grafo da rede com 5 nós e arestas bidirecionais."""
    G = nx.DiGraph()
    console.print("[bold blue]Criação do grafo com 5 nós e arestas bidirecionais:[/bold blue]")
    G.add_nodes_from(NODES)
    G.add_edges_from(EDGES)
    
    # Desenho do grafo
    tree = Tree("Rede Óptica")
    edge_id = 1
    for node in G.nodes:
        node_branch = tree.add(f"Nó {node}")
        for neighbor in G.neighbors(node):
            node_branch.add(f"Fibra {edge_id}: {node} -> {neighbor}")
            edge_id += 1
    console.print(tree)

    visualize_network(G)
    
    return G

def visualize_network(G):
    """Visualiza a topologia da rede óptica."""
    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15, font_weight='bold')
    plt.title("Topologia da Rede Óptica")
    plt.show()

def setup_simulation(env, G, duration, show_resources, load, allocation_algorithm):
    """Configura a simulação com geradores de lightpaths e controlador."""
    ps = Control(env, G, debug=True, tab=show_resources, allocation_algorithm=allocation_algorithm)
    console.print("[bold blue]Controlador criado e inicializado.[/bold blue]")

    # Criar os geradores de lightpaths
    generators = [LightPathGenerator(env, i, duration, load, numberNodes=5, node_range=range(1, 6)) for i in range(1, 6)]

    # Conectar os geradores de lightpaths ao controlador
    for pg in generators:
        pg.out = ps

    console.print("[bold blue]Geradores de lightpaths criados e conectados ao controlador.[/bold blue]")
    return ps, generators

def real_time_step(env, start_time):
    """Sincroniza a simulação com o tempo real."""
    while True:
        yield env.timeout(1)
        elapsed_sim_time = env.now
        elapsed_real_time = time.time() - start_time
        if elapsed_real_time < elapsed_sim_time:
            time.sleep(elapsed_sim_time - elapsed_real_time)

def collect_statistics(control):
    """Coleta e exibe estatísticas da simulação."""
    if not control.pkt_sent:
        console.print("[bold red]Nenhum pacote foi enviado durante a simulação.[/bold red]")
    else:
        table = Table(title="Estatísticas dos Pacotes")
        table.add_column("Pacote ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Origem", justify="right", style="magenta")
        table.add_column("Destino", justify="right", style="green")
        table.add_column("Slots Usados", justify="right", style="blue")
        table.add_column("Tempo de Envio", justify="right", style="red")
        table.add_column("Duração", justify="right", style="yellow")

        for pkt in control.pkt_sent:
            table.add_row(
                str(pkt.id),
                str(pkt.src),
                str(pkt.dst),
                str(pkt.nslots),
                f"{pkt.time:.2f}",
                f"{pkt.duration:.2f}"
            )

        console.print(table)
        console.print("[bold green]Coleta de estatísticas concluída.[/bold green]")

def analyze_performance(control):
    """Analisa o desempenho da simulação."""
    total_requests = len(control.pkt_sent) + len(control.pkt_lost)
    blocking_probability = len(control.pkt_lost) / total_requests if total_requests > 0 else 0
    console.print(f"[bold blue]Taxa de Bloqueio: {blocking_probability:.2f}[/bold blue]")

def get_simulation_parameters():
    """Obtém os parâmetros da simulação do usuário."""
    try:
        duration = float(input('Duração(s) >> '))
        show_resources = input('Mostrar recursos (1 para True, 0 para False) >> ') == '1'
        load = float(input('Carga de tráfego (0.0 a 1.0) >> '))
        allocation_algorithm = ALLOCATION_ALGORITHMS.get(
            input('Algoritmo de alocação (0 para first_fit, 1 para best_gap) >> '), "first_fit"
        )
        return duration, show_resources, load, allocation_algorithm
    except ValueError:
        console.print("[bold red]Erro: Por favor, insira um valor válido para a duração![/bold red]")
        return None

def main():
    """Função principal para configurar e executar a simulação."""
    # Criar o grafo da rede
    G = create_network()

    # Criar o ambiente SimPy
    env = simpy.Environment()
    console.print("[bold blue]Ambiente de simulação SimPy criado.[/bold blue]")

    # Obter parâmetros da simulação
    params = get_simulation_parameters()
    if params is None:
        return
    duration, show_resources, load, allocation_algorithm = params

    # Configurar a simulação
    ps, generators = setup_simulation(env, G, duration, show_resources, load, allocation_algorithm)

    # Sincronização com tempo real
    start_time = time.time()
    env.process(real_time_step(env, start_time))

    # Executar a simulação com Rich Live
    with Live(console=console, refresh_per_second=1) as live:
        while env.peek() < duration:
            elapsed_sim_time = env.now
            clock_panel = Panel(f"[bold cyan]Tempo Simulado: {elapsed_sim_time:.2f}s[/bold cyan]")
            live.update(clock_panel)
            env.step()

    console.print("[bold green]Simulação concluída.[/bold green]")

    # Coletar e exibir estatísticas
    collect_statistics(ps)
    analyze_performance(ps)

if __name__ == "__main__":
    main()