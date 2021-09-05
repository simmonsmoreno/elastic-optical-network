from matplotlib import pyplot as plt
from datetime import datetime
from tabulate import tabulate
import numpy as np
import networkx
import random
import simpy

# GLOBAL VARIABLES
PKT_SENTS = 0
SLOTS_NUMBER = 10
TXRX_NUMBER = 6
TASA_BLOQ = []


class LightPathRequest(object):
    def __init__(self, id, src, dst, time, duration, nslots):
        self.id = id
        self.src = src
        self.dst = dst
        self.time = time
        self.duration = duration
        self.nslots = nslots
        self.fim = self.time + self.duration

    def __repr__(self):
        return "[{}s] \t #{} \t nodo {} ==> nodo {} \t nslots={} \t d={}s \t f={}s".\
            format(round(self.time, 2), self.id, self.src, self.dst,
                   self.nslots, round(self.duration, 2), round(self.fim, 2))


class LigthPathGenerator(object):
    """ Genera paquetes con una distribución de tiempo de llegada dada.
        Establece la variable miembro "out" a la entidad que recibirá el paquete.
    """

    def __init__(self, id, avegLightpathDuration, numberNodes=5, load=0):
        self.id = id
        self.avegLightpathDuration = avegLightpathDuration
        self.timeBetweenReq = avegLightpathDuration / (load * (numberNodes-1))
        self.numberNodes = numberNodes
        self.load = load
        self.out = None
        self.action = env.process(self.run())

    # inicia el método run() como un proceso SimPy
    def run(self):
        """
            La función generadora utilizada en las simulaciones.
        """

        global PKT_SENTS

        while PKT_SENTS < 10:

            # esperar la próxima transmisión
            duration = random.expovariate(1.0/self.timeBetweenReq)

            # El tiempo entre peticiones que hace cada fuente, se calcula de
            # forma aleatoria con una variable de tipo exponencial con media
            yield env.timeout(random.expovariate(self.timeBetweenReq))

            # El nodoDestino de la peticion del lightpath se genera de forma aleatoria entre el resto de destinos
            destino = list(range(1, self.numberNodes+1))

            if self.id in destino:
                destino.remove(self.id)

            dst = random.choice(destino)
            nslots = random.randint(1, 3)
            now = env.now

            # LightPathRquest(self, id, src, dst, time, duration, nslots):
            p = LightPathRequest(PKT_SENTS, self.id, dst, now, duration, nslots)

            # Establece la variable miembro "out" a la entidad que recibirá el paquete.
            self.out.put(p)

            PKT_SENTS += 1

        self.out.put(None)


class Control(object):

    def __init__(self, network, debug=True, tab=True):
        self.network = network
        self.debug = debug
        self.tab = tab
        self.pkt_sent = []
        self.pkt_lost = []
        self.txrx = np.ndarray([network.number_of_nodes(), 2])
        self.slots = np.ndarray([network.number_of_edges(), SLOTS_NUMBER])

        self.txrx.fill(TXRX_NUMBER)             # considering that all node have # tx and rx
        self.slots.fill(True)                   # considering that all slots is disponible

    def put(self, pkt):
        if pkt != None:                         # if generator send any packet
            if self.debug:                      
                now = env.now              # get the environment current time  
                self.remove(now)                # check if some request is finish

                # check resources disponibility and them allocate
                disp, slot_used = self.allocate(pkt.src, pkt.dst, pkt.nslots)

                if disp:
                    pkt.slot_used = slot_used           # get the slots used by the packet
                    self.pkt_sent.append(pkt)           # save the packet in the list of sent packets
                    TASA_BLOQ.append(0)                 # Si el lightpath se ha establecido, guardamos un 0
                    
                    # print('\033[96m'"[{}]\t\t#{}\tt={}s\t\td={}s\t\tf={}s\t\t#slots={}\t\tnodo{} ==> nodo{}"'\033[0m' .format(round(env.now, 2), pkt.id, round(pkt.time, 2), round(pkt.duration, 2), round(pkt.time+pkt.duration, 2), pkt.nslots, pkt.src, pkt.dst))
                    print('\033[96m'"nodo{} ==> nodo{}\t\t#slots={}"'\033[0m' .format(pkt.src, pkt.dst, pkt.nslots))

                    # time.sleep(2)
                else:
                    print('\033[91m'"{} ==> {} #slots = {}"'\033[91m' .format(pkt.src, pkt.dst, pkt.nslots))
                    print('\033[91m''Unavailable resources. REQUEST LOST!''\033[91m')
                    self.pkt_lost.append(pkt)           # save the packet in the list of lost packets
                    TASA_BLOQ.append(1)                 # Si el lightpath NO se ha establecido (porque no hay transmisores, receptores o "slots"), guardamos un 1
                    # time.sleep(2)
                    return

        else:
            self.remove(None)                       # remove request after duration
        
        if self.tab:
            self.tabulate(self.txrx, self.slots)    # print the resources tables

    def remove(self, now):
        # remove request after duration
        pkt_sent = self.pkt_sent if now != None else sorted(
            self.pkt_sent, key=lambda x: x.time+x.duration)

        # time.sleep(2)

        if now != None:
            for p in pkt_sent:
                if (p.time + p.duration) < now:
                    self.pkt_sent.remove(p)

                    # increment the tx and rx of source node
                    self.txrx[p.src-1][0] += 1
                    self.txrx[p.dst-1][1] += 1

                    # set disponible the number of slots used
                    for i in range(len(p.slot_used)):
                        slo = p.slot_used[i]
                        self.slots[slo[0]][slo[1]] = True

                    print('\033[93m'"[{}]\t\t#{}\tFINISHED ::: #slots={}\t\tnodo{} ==> nodo{}"'\033[0m' .format(
                        round(p.time+p.duration, 2), p.id, p.nslots, p.src, p.dst))

        else:
            for p in pkt_sent:
                print('\033[93m'"[{}]\t\t#{}\tFINISHED"'\033[0m' .format(
                    round(p.time+p.duration, 2), p.id))

            self.pkt_sent.clear()
            
            self.txrx.fill(4)                   # considering that all node have 4 tx and rx
            self.slots.fill(True)               # considering that all slots is disponible

        # self.tabulate(self.txrx, self.slots)

    def allocate(self, src, dst, num_slots):
        
        edges = list(self.network.edges())      # list of edges of the network
        paths = []                              # list of nodes that are used e.g: 1->3 paths = [1,2,3]
        index = []                              # list of index of used fibers
        channels = []                           # list of index of slots availables in a fiber or conjunt of fibers
        slot_used = []                          # save the slots used by a packet
        disp = False

        paths = networkx.shortest_path(self.network, src, dst)          # get the shortest path from src to dst

        for i in range(len(paths)-1):
            if (paths[i], paths[i+1]) in edges:                         # if [1,2] is not in edges them use [2,1]
                index.append(edges.index((paths[i], paths[i+1])))       
            else:
                index.append(edges.index((paths[i+1], paths[i])))      

        # Check columns in which all slots are disponibles when src to dst use more than one fiber
        if len(paths) > 2:
            trans_slot = self.slots.T               
            for k in range(trans_slot.shape[0]):
                if np.all(trans_slot[k] == True):   # if colunm[k] is fill just by True
                    channels.append(k) 
        
        # Check rows in a fiber wich is available
        else:
            channels = [i for i in range(SLOTS_NUMBER) if self.slots[index][0][i] == True]
            

        if num_slots > 1:
            # channels = self.checkSlotsFirstFit(num_slots, channels)
            channels = self.checkSlotsBestGap(num_slots, channels)

        if channels == []:
            return False, []

        # decrement the number of slots
        for i in range(len(index)):
            for k in range(num_slots):
                for j in channels:
                    if self.slots[index[i]][j] == True and self.txrx[src-1][0] > 0 and self.txrx[dst-1][1] > 0:
                        self.slots[index[i]][j] = False
                        slot_used.append([index[i], j])
                        disp = True
                        break

        # decrement the tx of source node and the rx of dest node
        if disp and self.txrx[src-1][0] > 0 and self.txrx[dst-1][1] > 0:
            disp = disp and True
            self.txrx[src-1][0] -= 1
            self.txrx[dst-1][1] -= 1
        else:
            disp = False

        return disp, slot_used

    def tabulate(self, txrx, slots):
        headers_txrx = ["nodes", "tx", "rx"]
        headers_slots = ["fibers"]

        for i in range(SLOTS_NUMBER):
            headers_slots.append("slot " + str((i+1)))

        table_txrx = tabulate(txrx, headers_txrx, tablefmt="fancy_grid", showindex=self.network.nodes)
        # table_slots = tabulate(slots, headers_slots, tablefmt="fancy_grid")
        table_slots = tabulate(slots, headers_slots, tablefmt="fancy_grid", showindex=self.network.edges)

        print(table_txrx)
        print(table_slots)

    def checkSlotsFirstFit(self, n, l):
        l = sorted(l)
        for i in range(len(l)):
            sublist = l[i:n+i]
            if len(sublist) < n:
                return []
            consecutive = sorted(sublist) == list(range(min(sublist), max(sublist)+1))
            if consecutive:
                return sublist
        return []

    def checkSlotsBestGap(self, n_slot, lista):
        index = []
        sublist = []
        for i in range(len(lista)):
            try:
                if lista[i]+1 == lista[i+1]:
                    index.append(lista[i])
                    if i+1 == len(lista)-1:
                        index.append(lista[i+1])
                
                else:
                    if lista[i-1] == lista[i]-1:
                        index.append(lista[i])

                    if len(index) >= n_slot:
                        sublist.append(index)
                
                    index = []
                
                
            except:
                if len(index) >= n_slot:
                    sublist.append(index)

        if len(sublist):
            while True:
                for lista2 in sublist:
                    if len(lista2) == n_slot:
                        return lista2
                n_slot += 1
        else:
            return []


G = networkx.DiGraph() 

# network topology:
G.add_nodes_from([1,2,3,4,5])
G.add_edges_from([(1,2), (2,1), (1,4), (4,1), (2,3), (3,2), (2,5), (5,2), (3,5), (5,3), (4,5), (5,4)])

print(G.edges)

env = simpy.Environment()  # Crea el entorno SimPy

duration = float(input('Duration >> '))

# Crea el nodo control and pass the network topology
ps = Control(G, debug=True, tab=True)  # habilitar la depuración para una salida simple


# Crea el generador de paquetes
# LightpathRequestGenerator(self, env, id, avegLightpathDuration, numberNodes=5, load=0, flow_id=0):
pg1 = LigthPathGenerator(1, duration, load=0.5)
pg2 = LigthPathGenerator(2, duration, load=0.5)
pg3 = LigthPathGenerator(3, duration, load=0.5)
pg4 = LigthPathGenerator(4, duration, load=0.5)
pg5 = LigthPathGenerator(5, duration, load=0.5)

# # Conectar los generadores de paquetes y el sink
pg1.out = ps
pg2.out = ps
pg3.out = ps
pg4.out = ps
pg5.out = ps

env.run()  # Ejecutarlo

print(TASA_BLOQ)