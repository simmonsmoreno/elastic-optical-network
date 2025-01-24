import networkx as nx
import simpy
import time
from statsmodels.stats.proportion import proportion_confint
from components.light_path_control import Control
from components.light_path_generator import LightPathGenerator
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.tree import Tree
import matplotlib.pyplot as plt

console = Console()

# GLOBAL VARIABLES
PKT_SENTS = 0               # Variável global para o número de pacotes enviados
SLOTS_NUMBER = 320          # Número total de slots disponíveis
TXRX_NUMBER = 1000          # Número total de transmissores/receptores
TASA_BLOQ = []              # Lista para armazenar as taxas de bloqueio
DURATION = 5                # Duração da simulação
LOAD = 0.1                  # Carga da rede
NUM_MAX_SLOTS = 24          # Número máximo de slots por conexão
NUM_MAX_PET = 1000          # Número máximo de pacotes por conexão
NUM_ELIM = 100              # Número de elementos a serem eliminados da lista TASA_BLOQ

def create_network():
    """Cria o grafo da rede NSFNET com 14 nós e arestas bidirecionais."""
    G = nx.DiGraph()
    console.print("[bold blue]Criação do grafo NSFNET com 14 nós e arestas bidirecionais:[/bold blue]")
    G.add_nodes_from(range(14))  # Nós de 0 a 13
    edges = [(0,1), (0,2), (0,7), (1,0), (1,2), (1,3), (2,0), (2,1), (2,5), (3,1), (3,4), (3,10), (4,3), (4,5), (4,6), (5,2), (5,4), (5,9), (5,13), (6,4), (6,7), (7,0), (7,6), (7,8), (8,7), (8,9), (8,11), (8,12), (9,5), (9,8), (10,3), (10,11), (10,12), (11,8), (11,10), (11,13), (12,8), (12,10), (12,13), (13,5), (13,11), (13,12)]
    G.add_edges_from(edges)
    
    # Desenho do grafo
    tree = Tree("Rede Óptica NSFNET")
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
    """Visualiza a topologia da rede óptica NSFNET."""
    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15, font_weight='bold')
    plt.title("Topologia da Rede Óptica NSFNET")
    plt.show()

def setup_simulation(env, G, duration, show_resources, load, allocation_algorithm):
    """Configura a simulação com geradores de lightpaths e controlador."""
    ps = Control(env, G, debug=True, tab=show_resources, allocation_algorithm=allocation_algorithm)  # Habilitar a depuração para uma saída simples
    console.print("[bold blue]Controlador criado e inicializado.[/bold blue]")

    # Criar os geradores de lightpaths
    generators = [LightPathGenerator(env, i, duration, load, numberNodes=14) for i in range(14)]

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
        table.add_column("Caminho", justify="right", style="white")

        for pkt in control.pkt_sent:
            table.add_row(
                str(pkt.id),
                str(pkt.src),
                str(pkt.dst),
                str(pkt.nslots),
                f"{pkt.time:.2f}",
                f"{pkt.duration:.2f}",
                " -> ".join(map(str, pkt.path))
            )

        console.print(table)
        console.print("[bold green]Coleta de estatísticas concluída.[/bold green]")

def analyze_performance(control):
    """Analisa o desempenho da simulação."""
    total_requests = len(control.pkt_sent) + len(control.pkt_lost)
    blocking_probability = len(control.pkt_lost) / total_requests if total_requests > 0 else 0
    console.print(f"[bold blue]Taxa de Bloqueio: {blocking_probability:.2f}[/bold blue]")

    # Calcular intervalo de confiança
    count = control.pkt_lost.count(1)
    nobs = total_requests
    if nobs > 0:
        ic = proportion_confint(count, nobs, alpha=0.05, method='normal')
        console.print(f"[bold blue]Intervalo de Confiança: {ic}[/bold blue]")
    else:
        console.print("[bold red]Nenhuma observação disponível para calcular a proporção.[/bold red]")

def main():
    """Função principal para configurar e executar a simulação."""
    # Criar o grafo da rede
    G = create_network()

    # Criar o ambiente SimPy
    env = simpy.Environment()
    console.print("[bold blue]Ambiente de simulação SimPy criado.[/bold blue]")

    # Definir a duração da simulação
    try:
        duration = float(input('Duração(s) >> '))
        show_resources_input = input('Mostrar recursos (1 para True, 0 para False) >> ')
        show_resources = show_resources_input == '1'    
        load = float(input('Carga de tráfego (0.0 a 1.0) >> '))
        allocation_algorithm_input = input('Algoritmo de alocação (0 para first_fit, 1 para best_gap) >> ')
        if allocation_algorithm_input == '0':
            allocation_algorithm = "first_fit"
        elif allocation_algorithm_input == '1':
            allocation_algorithm = "best_gap"
        else:
            console.print("[bold red]Erro: Inserido um valor inválido! first_fit assumido como algoritmo padrão[/bold red]")
            allocation_algorithm = "first_fit"
    except ValueError:
        console.print("[bold red]Erro: Por favor, insira um valor válido para a duração![/bold red]")
        return

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