import networkx as nx
import simpy
import time
from components.light_path_control import Control
from components.light_path_generator import LightPathGenerator as Generator
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

TASA_BLOQ = []

console = Console()

def create_network():
    """Cria o grafo da rede com 5 nós e arestas bidirecionais."""
    G = nx.DiGraph()
    console.print("Criação do grafo com 5 nós e arestas bidirecionais.", style="bold green")
    G.add_nodes_from([1, 2, 3, 4, 5])
    G.add_edges_from([(1, 2), (2, 1), (1, 4), (4, 1), (2, 3), (3, 2), (2, 5), (5, 2), (3, 5), (5, 3), (4, 5), (5, 4)])
    console.print(f"Arestas do grafo: {G.edges}", style="bold green")
    return G

def setup_simulation(env, G, duration):
    """Configura a simulação com geradores de lightpaths e controlador."""
    ps = Control(env, G, debug=True, tab=False)  # Habilitar a depuração para uma saída simples
    console.print("Controlador criado e inicializado.", style="bold green")

    # Criar os geradores de lightpaths
    generators = [Generator(env, i, duration, load=0.5, numberNodes=5) for i in range(1, 6)]

    # Conectar os geradores de lightpaths ao controlador
    for pg in generators:
        pg.out = ps

    console.print("Geradores de lightpaths criados e conectados ao controlador.", style="bold green")
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
    console.print("Coleta de estatísticas concluída.", style="bold green")

def main():
    """Função principal para configurar e executar a simulação."""
    # Criar o grafo da rede
    G = create_network()

    # Criar o ambiente SimPy
    env = simpy.Environment()
    console.print("Ambiente de simulação SimPy criado.", style="bold green")

    # Definir a duração da simulação
    try:
        duration = float(input('Duration >> '))
    except ValueError:
        console.print("[bold red]Erro: Por favor, insira um valor válido para a duração![/bold red]")
        return

    # Configurar a simulação
    ps, generators = setup_simulation(env, G, duration)

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

    console.print("Simulação concluída.", style="bold green")

    # Coletar e exibir estatísticas
    collect_statistics(ps)

if __name__ == "__main__":
    main()