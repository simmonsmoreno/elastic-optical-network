"""
Simulação de Redes Ópticas com SimPy.
Cria geradores e receptores de pacotes para simular eventos discretos.
Adiciona métricas detalhadas, sincronização de tempo real e visualização interativa no terminal.
"""

import simpy
import time
from random import expovariate
from components.light_path_generator import LightPathGenerator
from components.packet_sink import PacketSink
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.tree import Tree

console = Console()

def distDuration():
    """
    Calcula a duração do lightpath como uma variável aleatória exponencial.
    Média: 6 unidades de tempo.
    """
    return expovariate(1 / 6)

def distSize():
    """
    Calcula o tamanho do pacote como uma variável aleatória exponencial.
    Média: 100 unidades.
    """
    return expovariate(0.01)

def real_time_step(env, start_time):
    """
    Sincroniza a simulação com o tempo real.
    Garante que eventos no tempo simulado sejam exibidos de forma sincronizada.
    """
    while True:
        yield env.timeout(1)
        elapsed_sim_time = env.now
        elapsed_real_time = time.time() - start_time
        if elapsed_real_time < elapsed_sim_time:
            time.sleep(elapsed_sim_time - elapsed_real_time)

def build_network_tree(num_generators, num_sinks):
    """
    Cria uma representação da rede óptica em forma de árvore usando Rich.
    """
    tree = Tree("Rede Óptica")
    generators_branch = tree.add("Geradores")
    sinks_branch = tree.add("Receptores")
    for i in range(num_generators):
        generators_branch.add(f"Gerador {i}")
    for i in range(num_sinks):
        sinks_branch.add(f"Receptor {i}")
    return tree

def main(duration, load, num_generators, num_sinks):
    """
    Função principal para configurar e executar a simulação.
    """
    env = simpy.Environment()

    # Criar geradores e receptores
    sinks = [PacketSink(env, rec_arrivals=True, debug=True) for _ in range(num_sinks)]
    generators = [LightPathGenerator(env, i, duration, load=load) for i in range(num_generators)]

    for pg in generators:
        pg.out = sinks[pg.id % num_sinks]  # Distribui pacotes entre os sinks

    # Sincronização com tempo real
    start_time = time.time()
    env.process(real_time_step(env, start_time))

    # Exibição da rede
    tree = build_network_tree(num_generators, num_sinks)
    console.print(tree)

    # Executar a simulação com Rich Live
    with Live(console=console, refresh_per_second=1) as live:
        while env.peek() < duration:
            elapsed_sim_time = env.now
            clock_panel = Panel(f"[bold cyan]Tempo Simulado: {elapsed_sim_time:.2f}s[/bold cyan]")
            live.update(clock_panel)
            env.step()

    # Coletar e exibir estatísticas
    table = Table(title="Estatísticas dos Receptores")
    table.add_column("Receptor", justify="right", style="cyan", no_wrap=True)
    table.add_column("Pacotes Recebidos", justify="right", style="magenta")
    table.add_column("Tamanho Total dos Pacotes", justify="right", style="green")
    table.add_column("Tempo Médio de Chegada", justify="right", style="blue")
    table.add_column("Tempo Médio de Espera", justify="right", style="red")
    table.add_column("Taxa de Perda (%)", justify="right", style="yellow")

    for i, sink in enumerate(sinks):
        packets_lost = sink.packets_lost if hasattr(sink, "packets_lost") else 0
        loss_rate = (packets_lost / (sink.packets_rec + packets_lost) * 100) if (sink.packets_rec + packets_lost) > 0 else 0
        table.add_row(
            str(i),
            str(sink.packets_rec),
            str(sink.bytes_rec),
            f"{sum(sink.arrivals) / len(sink.arrivals) if sink.arrivals else 0:.2f}",
            f"{sum(sink.waits) / len(sink.waits) if sink.waits else 0:.2f}",
            f"{loss_rate:.2f}"
        )

    console.print(table)

if __name__ == "__main__":
    # Solicita parâmetros ao usuário
    try:
        duration = float(input("Informe a duração da simulação (s): "))
        load = float(input("Informe a carga do gerador (0 a 1): "))
        num_generators = int(input("Informe o número de geradores: "))
        num_sinks = int(input("Informe o número de receptores: "))
    except ValueError:
        console.print("[bold red]Erro: Por favor, insira valores válidos![/bold red]")
        exit(1)

    main(duration, load, num_generators, num_sinks)
