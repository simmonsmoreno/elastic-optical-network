"""
    Ejemplo simple de GeneradorPaquete y PacketSink del módulo Components. 
    Crea dos generadores de paquetes de velocidad exponcencial y los conecta a un sink.
"""
import simpy
from random import expovariate
from components.light_path_generator import LightPathGenerator
from components.packet_sink import PacketSink

def distDuration():  # Distribución de llegada exponencial para los generadores
    return expovariate(1/6) # La duración del lightpath se calcula como una variable aleatoria de tipo exponencial con media

def distSize():
    return expovariate(0.01)

env = simpy.Environment()  # Crea el entorno SimPy

# Crea el generador de paquetes e el sink
ps = PacketSink(env, debug=True)  # habilitar la depuración para una salida simple

duration = float(input('Duration >> '))

pg1 = LightPathGenerator(env, 1, duration, load=0.5)

# Conectar los generadores de paquetes y el sink
pg1.out = ps

env.run()  # Ejecutarlo
