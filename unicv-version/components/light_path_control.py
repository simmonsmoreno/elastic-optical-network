import numpy as np
import networkx as nx
from tabulate import tabulate

class Control(object):
    def __init__(self, env, network, debug=True, tab=True):
        self.env = env
        self.network = network
        self.debug = debug
        self.tab = tab
        self.pkt_sent = []
        self.pkt_lost = []
        self.txrx = np.ndarray([network.number_of_nodes(), 2])
        self.slots = np.ndarray([network.number_of_edges(), 10]) 

        self.txrx.fill(10)  
        self.slots.fill(True)

    def put(self, pkt):
        if pkt is not None:
            if self.debug:
                now = self.env.now
                self.remove(now)

                disp, slot_used = self.allocate(pkt.src, pkt.dst, pkt.nslots)

                if disp:
                    pkt.slot_used = slot_used
                    self.pkt_sent.append(pkt)
                    print('\033[96m'"nodo{} ==> nodo{}\t\t#slots={}"'\033[0m'.format(pkt.src, pkt.dst, pkt.nslots))
                else:
                    print('\033[91m'"{} ==> {} #slots = {}"'\033[91m'.format(pkt.src, pkt.dst, pkt.nslots))
                    print('\033[91m''Unavailable resources. REQUEST LOST!''\033[91m')
                    self.pkt_lost.append(pkt)
        else:
            self.remove(None)
        
        if self.tab:
            self.tabulate(self.txrx, self.slots)

    def remove(self, now):
        pkt_sent = self.pkt_sent if now is not None else sorted(self.pkt_sent, key=lambda x: x.time + x.duration)

        if now is not None:
            for p in pkt_sent:
                if (p.time + p.duration) < now:
                    self.pkt_sent.remove(p)
                    self.txrx[p.src-1][0] += 1
                    self.txrx[p.dst-1][1] += 1
                    for slo in p.slot_used:
                        self.slots[slo[0]][slo[1]] = True
                    print('\033[93m'"[{}]\t\t#{}\tFINISHED ::: #slots={}\t\tnodo{} ==> nodo{}"'\033[0m'.format(round(p.time + p.duration, 2), p.id, p.nslots, p.src, p.dst))
        else:
            self.pkt_sent.clear()
            self.txrx.fill(10)
            self.slots.fill(True)

    def allocate(self, src, dst, num_slots):
        edges = list(self.network.edges())
        paths = []
        index = []
        channels = []
        slot_used = []
        disp = False

        paths = nx.shortest_path(self.network, src, dst)

        for i in range(len(paths) - 1):
            if (paths[i], paths[i + 1]) in edges:
                index.append(edges.index((paths[i], paths[i + 1])))
            else:
                index.append(edges.index((paths[i + 1], paths[i])))

        if len(paths) > 2:
            trans_slot = self.slots.T
            for k in range(trans_slot.shape[0]):
                if np.all(trans_slot[k] == True):
                    channels.append(k)
        else:
            channels = [i for i in range(10) if self.slots[index][0][i] == True]

        if num_slots > 1:
            channels = self.checkSlotsBestGap(num_slots, channels)

        if not channels:
            return False, []

        for i in range(len(index)):
            for k in range(num_slots):
                for j in channels:
                    if self.slots[index[i]][j] == True and self.txrx[src-1][0] > 0 and self.txrx[dst-1][1] > 0:
                        self.slots[index[i]][j] = False
                        slot_used.append([index[i], j])
                        disp = True
                        break

        if disp and self.txrx[src-1][0] > 0 and self.txrx[dst-1][1] > 0:
            self.txrx[src-1][0] -= 1
            self.txrx[dst-1][1] -= 1
        else:
            disp = False

        return disp, slot_used

    def tabulate(self, txrx, slots):
        headers_txrx = ["nodes", "tx", "rx"]
        headers_slots = ["fibers"]

        for i in range(10):
            headers_slots.append("slot " + str((i + 1)))

        table_txrx = tabulate(txrx, headers_txrx, tablefmt="fancy_grid", showindex=self.network.nodes)
        table_slots = tabulate(slots, headers_slots, tablefmt="fancy_grid", showindex=self.network.edges)

        print(table_txrx)
        print(table_slots)

    def checkSlotsFirstFit(self, n, l):
        l = sorted(l)
        for i in range(len(l)):
            sublist = l[i:n + i]
            if len(sublist) < n:
                return []
            consecutive = sorted(sublist) == list(range(min(sublist), max(sublist) + 1))
            if consecutive:
                return sublist
        return []

    def checkSlotsBestGap(self, n_slot, lista):
        index = []
        sublist = []
        for i in range(len(lista)):
            try:
                if lista[i] + 1 == lista[i + 1]:
                    index.append(lista[i])
                    if i + 1 == len(lista) - 1:
                        index.append(lista[i + 1])
                else:
                    if lista[i - 1] == lista[i] - 1:
                        index.append(lista[i])
                    if len(index) >= n_slot:
                        sublist.append(index)
                    index = []
            except:
                if len(index) >= n_slot:
                    sublist.append(index)

        if sublist:
            while True:
                for lista2 in sublist:
                    if len(lista2) == n_slot:
                        return lista2
                n_slot += 1
        else:
            return []
