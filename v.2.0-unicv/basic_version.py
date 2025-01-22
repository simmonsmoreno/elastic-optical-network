"""
    Simulação de eventos discretos com simpy.
    Cria um gerador de pacotes (LightPathGenerator) e um receptor (PacketSink).
    O gerador envia pacotes com distribuição exponencial de tempo de chegada.
    O receptor registra e coleta estatísticas dos pacotes recebidos.
    Executa por um tempo especificado e imprime as estatísticas.
"""

import simpy
from random import expovariate
from components.light_path_generator import LightPathGenerator
from components.packet_sink import PacketSink

def distDuration():
    return expovariate(1/6)  # Duração do lightpath com média de 6 unidades de tempo

def distSize():
    return expovariate(0.01)  # Tamanho do pacote com média de 100 unidades

def main(duration=10):
    env = simpy.Environment()

    # Cria um receptor de pacotes
    ps = PacketSink(env, debug=True)        

    # Cria um gerador de pacotes
    pg1 = LightPathGenerator(env, 1, duration, load=0.5) 

    # Conecta o gerador de pacotes ao receptor de pacotes   
    pg1.out = ps  

    # Executa a simulação por um tempo especificado      
    env.run(until=duration) 

if __name__ == "__main__":
    duration = float(input('Duration >> '))
    main(duration)
