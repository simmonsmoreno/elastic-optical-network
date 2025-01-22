import networkx
import simpy
from statsmodels.stats.proportion import proportion_confint
from components.light_path_control import Control
from components.light_path_generator import LightPathGenerator

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

G = networkx.DiGraph()      # Criação de um grafo direcionado vazio

# Adiciona nós e arestas ao grafo
G.add_nodes_from(range(14))
G.add_edges_from([(0,1), (0,2), (0,7), (1,0), (1,2), (1,3), (2,0), (2,1), (2,5), (3,1), (3,4), (3,10), (4,3), (4,5), (4,6), (5,2), (5,4), (5,9), (5,13), (6,4), (6,7), (7,0), (7,6), (7,8), (8,7), (8,9), (8,11), (8,12), (9,5), (9,8), (10,3), (10,11), (10,12), (11,8), (11,10), (11,13), (12,8), (12,10), (12,13), (13,5), (13,11), (13,12)])

env = simpy.Environment()   # Criação do ambiente de simulação

print("===============================================================================")
print('Load = {}' .format(LOAD))

ps = Control(env, G, debug=True, tab=True)  # Criação do objeto de controle

generators = []
for i in range(14):
    generator = LightPathGenerator(env, i, DURATION, load=LOAD)  # Criação de geradores de caminhos de luz
    generator.out = ps  # Define o objeto de controle como saída dos geradores
    generators.append(generator)

env.run()  # Executa a simulação

TASA_BLOQ = TASA_BLOQ[NUM_ELIM:-NUM_ELIM:1]  # Remove os elementos iniciais e finais da lista TASA_BLOQ

count = TASA_BLOQ.count(1)  # Conta o número de conexões bloqueadas
nobs = len(TASA_BLOQ)  # Obtém o número total de conexões tentadas

if nobs > 0:
    ic = proportion_confint(count, nobs, alpha=0.05, method='normal')  # Calcula o intervalo de confiança da proporção
    average = sum(TASA_BLOQ) / nobs  # Calcula a taxa média de bloqueio
    print(average)
    print(ic)
else:
    print("Nenhuma observação disponível para calcular a proporção.")
