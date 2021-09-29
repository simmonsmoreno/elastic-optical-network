"""
    Ejemplo simple de GeneradorPaquete y PacketSink del módulo Components. 
    Crea dos generadores de paquetes de velocidad exponcencial y los conecta a un sink.
"""
import simpy
from random import expovariate
from Components import LightpathRequestGenerator, PacketSink

def distDuration():  # Distribución de llegada exponencial para los generadores
    return expovariate(1/6) # La duración del lightpath se calcula como una variable aleatoria de tipo exponencial con media

def distSize():
    return expovariate(0.01)

env = simpy.Environment()  # Crea el entorno SimPy

# Crea el generador de paquetes e el sink
ps = PacketSink(env, debug=True)  # habilitar la depuración para una salida simple

duration = float(input('Duration >> '))

# LightpathRequestGenerator(self, env, id, avegLightpathDuration, numberNodes=5, load=0, flow_id=0):
pg1 = LightpathRequestGenerator(env, 1, duration, load=0.5)
# pg2 = LightpathRequestGenerator(env, 2, distSize, distDuration(), load=6)
# pg3 = LightpathRequestGenerator(env, 3, distSize, distDuration(), load=6)
# pg4 = LightpathRequestGenerator(env, 4, distSize, distDuration(), load=6)
# pg5 = LightpathRequestGenerator(env, 5, distSize, distDuration(), load=6)

# Conectar los generadores de paquetes y el sink
pg1.out = ps
# pg2.out = ps
# pg3.out = ps
# pg4.out = ps
# pg5.out = ps

env.run()  # Ejecutarlo
