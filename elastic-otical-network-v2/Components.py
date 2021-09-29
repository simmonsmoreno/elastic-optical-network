import simpy
import random

packets_sent = 0

class LightpathRequest(object):
    def __init__(self, time, id, src, dst, flow_id=0):
        self.time = time
        # self.size = size
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id

    def __repr__(self):
        return "id: {}, nodo origem: {}, nodo destino: {}, tiempo inicio: {}s".\
            format(self.id, self.src, self.dst, round(self.time, 2))


class LightpathRequestGenerator(object):
    """ Genera paquetes con una distribución de tiempo de llegada dada.
        Establece la variable miembro "out" a la entidad que recibirá el paquete.
    """
    def __init__(self, env, id, avegLightpathDuration, numberNodes=5, load=0, flow_id=0):
        self.id = id
        self.env = env
        self.avegLightpathDuration = random.expovariate(avegLightpathDuration)
        self.timeBetweenReq = avegLightpathDuration / (load * (numberNodes-1))
        # self.size = size
        self.numberNodes = numberNodes
        self.load = load
        self.out = None
        self.action = env.process(self.run())  # inicia el método run() como un proceso SimPy
        self.flow_id = flow_id

    def run(self):
        """
            La función generadora utilizada en las simulaciones.
        """

        print('Average Light Path Duration Generator %d >> %.2f seconds' % (self.id, round(self.avegLightpathDuration, 2)))
        print('Time Between Request Generator %d >> %.2f seconds' % (self.id, round(self.timeBetweenReq, 2)))
        print('--------------------------------------------------------------')

        # exit()
        global packets_sent
        

        # La duración del lightpath se calcula como una variable aleatoria de tipo exponencial con media
        while packets_sent < 5:
            # esperar la próxima transmisión
            
            # El tiempo entre peticiones que hace cada fuente, se calcula de forma aleatoria con una variable de tipo exponencial con media
            yield self.env.timeout(self.timeBetweenReq)
            packets_sent += 1

            # El nodoDestino de la peticion del lightpath se genera de forma aleatoria entre el resto de destinos. 
            # La fuente 1 no puede generar peticiones cuyo nodo destino sea 1 y así con el resto de peticiones.
            destino = random.sample(range(1, self.numberNodes), self.numberNodes-1)
            if self.id in destino:
                destino.remove(self.id)
    
            # LightpathRequest(self, time, id, src, dst, flow_id=0):
            p = LightpathRequest(self.env.now, packets_sent, self.id, random.choice(destino), flow_id=self.flow_id)

            # Establece la variable miembro "out" a la entidad que recibirá el paquete.
            self.out.put(p) 


class PacketSink(object):
    """ Recibe los paquetes y recoge la información de los retrasos en la
        lista de esperas. Podemos utilizar esta lista para ver las estadísticas de retardo.

        Parámetros
        ----------
        env : simpy.Environment
            el entorno de la simulación
        debug : boolean
            si es verdadero, se imprimirá el contenido de cada paquete a medida que se reciba.
        rec_arrivals : boolean
            si es verdadero, se registrarán las llegadas
        absolute_arrivals : boolean
            si es verdadero se registrarán los tiempos de llegada absolutos, en caso contrario se registrará el tiempo entre llegadas consecutivas.
        rec_waits : boolean
            si es verdad se registra el tiempo de espera experimentado por cada paquete
        selector: una función que toma un paquete y devuelve un booleano
            utilizado para las estadísticas selectivas. Por defecto ninguno.

    """
    def __init__(self, env, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None):
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits = []
        self.arrivals = []
        self.debug = debug
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector
        self.last_arrival = 0.0

    def put(self, pkt):
        if not self.selector or self.selector(pkt):
            now = self.env.now
            if self.rec_waits:
                self.waits.append(self.env.now - pkt.time)
            if self.rec_arrivals:
                if self.absolute_arrivals:
                    self.arrivals.append(now)
                else:
                    self.arrivals.append(now - self.last_arrival)
                self.last_arrival = now
            self.packets_rec += 1
            # self.bytes_rec += pkt.size
            if self.debug:
                print(pkt)

