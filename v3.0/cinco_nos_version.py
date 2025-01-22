import networkx as nx
import simpy
import logging
from components.light_path_control import Control
from components.light_path_generator import LightPathGenerator as Generator

TASA_BLOQ = []

# Configuração básica do logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_network():
    """Cria o grafo da rede com 5 nós e arestas bidirecionais."""
    G = nx.DiGraph()
    logging.info("Criação do grafo com 5 nós e arestas bidirecionais.")
    G.add_nodes_from([1, 2, 3, 4, 5])
    G.add_edges_from([(1, 2), (2, 1), (1, 4), (4, 1), (2, 3), (3, 2), (2, 5), (5, 2), (3, 5), (5, 3), (4, 5), (5, 4)])
    logging.info(f"Arestas do grafo: {G.edges}")
    return G

def setup_simulation(env, G, duration):
    """Configura a simulação com geradores de lightpaths e controlador."""
    ps = Control(env, G, debug=True, tab=False)  # Habilitar a depuração para uma saída simples
    logging.info("Controlador criado e inicializado.")

    # Criar os geradores de lightpaths
    generators = [Generator(env, i, duration, load=0.5, numberNodes=5) for i in range(1, 6)]

    # Conectar os geradores de lightpaths ao controlador
    for pg in generators:
        pg.out = ps

    logging.info("Geradores de lightpaths criados e conectados ao controlador.")
    return ps, generators

def collect_statistics():
    """Coleta e exibe estatísticas da simulação."""
    # Aqui você pode adicionar código para coletar e exibir estatísticas da simulação
    logging.info("Coleta de estatísticas concluída.")

def main():
    """Função principal para configurar e executar a simulação."""
    # Criar o grafo da rede
    G = create_network()

    # Criar o ambiente SimPy
    env = simpy.Environment()
    logging.info("Ambiente de simulação SimPy criado.")

    # Definir a duração da simulação
    try:
        duration = float(input('Duration >> '))
    except ValueError:
        logging.error("Erro: Por favor, insira um valor válido para a duração!")
        return

    # Configurar a simulação
    ps, generators = setup_simulation(env, G, duration)

    # Executar a simulação
    env.run(until=duration)
    logging.info("Simulação concluída.")

    # Coletar e exibir estatísticas
    collect_statistics()

if __name__ == "__main__":
    main()