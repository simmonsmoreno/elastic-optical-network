import networkx
import simpy
import logging

from components.light_path_control import Control
from components.light_path_generator import LightPathGenerator as Generator

TASA_BLOQ = []

# Configuração básica do logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Criar o grafo da rede
G = networkx.DiGraph()
logging.info("Criação do grafo com 5 nós e arestas bidirecionais.")

# Topologia da rede:
G.add_nodes_from([1, 2, 3, 4, 5])
G.add_edges_from([(1, 2), (2, 1), (1, 4), (4, 1), (2, 3), (3, 2), (2, 5), (5, 2), (3, 5), (5, 3), (4, 5), (5, 4)])

logging.info(f"Arestas do grafo: {G.edges}")

# Criar o ambiente SimPy
env = simpy.Environment()
logging.info("Ambiente de simulação SimPy criado.")

# Definir a duração da simulação
duration = float(input('Duration >> '))

# Criar o controlador e passar a topologia da rede e o ambiente de simulação
ps = Control(env, G, debug=True, tab=False)  # Habilitar a depuração para uma saída simples
logging.info("Controlador criado e inicializado.")

# Criar os geradores de lightpaths
pg1 = Generator(env, 1, duration, load=0.5, numberNodes=5)
pg2 = Generator(env, 2, duration, load=0.5, numberNodes=5)
pg3 = Generator(env, 3, duration, load=0.5, numberNodes=5)
pg4 = Generator(env, 4, duration, load=0.5, numberNodes=5)
pg5 = Generator(env, 5, duration, load=0.5, numberNodes=5)

# Conectar os geradores de lightpaths ao controlador
pg1.out = ps
pg2.out = ps
pg3.out = ps
pg4.out = ps
pg5.out = ps

logging.info("Geradores de lightpaths criados e conectados ao controlador.")

# Executar a simulação
env.run(until=duration)
logging.info("Simulação concluída.")

# print(TASA_BLOQ)