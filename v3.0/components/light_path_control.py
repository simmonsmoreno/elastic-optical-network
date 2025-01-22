import numpy as np
import networkx as nx
from tabulate import tabulate
from rich.console import Console
from rich.table import Table

console = Console()

class Control(object):
    def __init__(self, env, network, debug=True, tab=True):
        """
        Inicializa o controlador de lightpaths.
        
        Args:
            env (simpy.Environment): O ambiente de simulação.
            network (networkx.Graph): O grafo da rede.
            debug (bool): Habilita ou desabilita mensagens de depuração.
            tab (bool): Habilita ou desabilita a tabulação das tabelas.
        """
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
        """
        Processa um pacote, alocando recursos ou registrando a perda do pacote.
        
        Args:
            pkt (Packet): O pacote a ser processado.
        """
        if pkt is not None:
            if self.debug:
                now = self.env.now
                self.remove(now)

                disp, slot_used, path = self.allocate(pkt.src, pkt.dst, pkt.nslots)

                if disp:
                    pkt.slot_used = slot_used
                    self.pkt_sent.append(pkt)
                    print('\033[97m' + "[{}sec] Pacote Enviado: \t id #{} \t\t Nó {} -> Nó {} \t\t #slots usados = {} \t duracao = {}sec \t caminho = {}".format(round(pkt.time, 2), pkt.id, pkt.src, pkt.dst, pkt.nslots, round(pkt.duration, 2), path) + '\033[0m')
                else:
                    print('\033[91m' + "[{}sec] Pacote Perdido: \t id #{} \t\t Nó {} -> Nó {} \t\t #slots solicitados = {} \t duracao = {}sec".format(round(pkt.time, 2), pkt.id, pkt.src, pkt.dst, pkt.nslots, round(pkt.duration, 2)) + '\033[91m')
                    print('\033[91m' + '\tRECURSOS NÃO DISPONÍVEIS!' + '\033[91m')
                    self.pkt_lost.append(pkt)
        else:
            self.remove(None)
        
        if self.tab:
            self.display_resources(self.txrx, self.slots)

    def remove(self, now):
        """
        Remove pacotes cujo tempo de duração expirou.
        
        Args:
            now (float): O tempo atual da simulação.
        """
        pkt_sent = self.pkt_sent if now is not None else sorted(self.pkt_sent, key=lambda x: x.time + x.duration)

        if now is not None:
            for p in pkt_sent:
                if (p.time + p.duration) < now:
                    self.pkt_sent.remove(p)
                    self.txrx[p.src-1][0] += 1
                    self.txrx[p.dst-1][1] += 1
                    for slo in p.slot_used:
                        self.slots[slo[0]][slo[1]] = True
                    print('\033[93m' + "[{}sec] TEMPO EXPIRADO \t id #{} \t\t Nó {} -> Nó {} \t\t #slots libertados = {}".format(round(p.time + p.duration, 2), p.id, p.src, p.dst, p.nslots) + '\033[0m')
        else:
            self.pkt_sent.clear()
            self.txrx.fill(10)
            self.slots.fill(True)

    def allocate(self, src, dst, num_slots):
        """
        Aloca recursos para um pacote.
        
        Args:
            src (int): O nó de origem.
            dst (int): O nó de destino.
            num_slots (int): O número de slots necessários.
        
        Returns:
            bool: Indica se a alocação foi bem-sucedida.
            list: Lista de slots usados.
            list: Caminho utilizado.
        """
        edges = list(self.network.edges())
        paths = nx.shortest_path(self.network, src, dst)
        index = self.get_edge_indices(paths, edges)
        channels = self.get_available_channels(paths, index)

        if num_slots > 1:
            channels = self.checkSlotsBestGap(num_slots, channels)

        if not channels:
            return False, [], paths

        disp, slot_used = self.allocate_slots(src, dst, num_slots, index, channels)
        return disp, slot_used, paths
    
    def get_edge_indices(self, paths, edges):
        """
        Obtém os índices das arestas no caminho.
        
        Args:
            paths (list): Lista de nós no caminho.
            edges (list): Lista de arestas na rede.
        
        Returns:
            list: Lista de índices das arestas.
        """
        index = []
        for i in range(len(paths) - 1):
            if (paths[i], paths[i + 1]) in edges:
                index.append(edges.index((paths[i], paths[i + 1])))
            else:
                index.append(edges.index((paths[i + 1], paths[i])))
        return index
    
    def get_available_channels(self, paths, index):
        """
        Obtém os canais disponíveis para alocação.
        
        Args:
            paths (list): Lista de nós no caminho.
            index (list): Lista de índices das arestas.
        
        Returns:
            list: Lista de canais disponíveis.
        """
        if len(paths) > 2:
            trans_slot = self.slots.T
            channels = [k for k in range(trans_slot.shape[0]) if np.all(trans_slot[k])]
        else:
            channels = [i for i in range(10) if self.slots[index][0][i]]
        return channels

    def allocate_slots(self, src, dst, num_slots, index, channels):
        """
        Aloca slots para um pacote.
        
        Args:
            src (int): O nó de origem.
            dst (int): O nó de destino.
            num_slots (int): O número de slots necessários.
            index (list): Lista de índices das arestas.
            channels (list): Lista de canais disponíveis.
        
        Returns:
            bool: Indica se a alocação foi bem-sucedida.
            list: Lista de slots usados.
        """
        slot_used = []
        disp = False

        for i in range(len(index)):
            for k in range(num_slots):
                for j in channels:
                    if self.slots[index[i]][j] and self.txrx[src-1][0] > 0 and self.txrx[dst-1][1] > 0:
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

    def display_resources(self, txrx, slots):
        """
        Exibe as tabelas de tx/rx e slots.
        
        Args:
            txrx (ndarray): Matriz de tx/rx.
            slots (ndarray): Matriz de slots.
        """
        if self.debug:

            console.print("\n")
            
            # Tabela de tx/rx
            table_txrx = Table(title="Recursos dos Nós (Tx/Rx)", show_header=True, header_style="bold magenta")
            table_txrx.add_column("Nó", justify="right")
            table_txrx.add_column("Tx", justify="right")
            table_txrx.add_column("Rx", justify="right")

            for i, (tx, rx) in enumerate(txrx, start=1):
                table_txrx.add_row(str(i), str(int(tx)), str(int(rx)))

            # Tabela de slots
            table_slots = Table(title="Recursos das Fibras (Slots)", show_header=True, header_style="bold magenta")
            table_slots.add_column("Fibra", justify="right")
            for i in range(slots.shape[1]):
                table_slots.add_column(f"Slot {i+1}", justify="right")

            for i, row in enumerate(slots, start=1):
                table_slots.add_row(str(i), *[str(int(slot)) for slot in row])

            console.print(table_txrx)
            console.print(table_slots)
            console.print("\n")

    def checkSlotsFirstFit(self, n, l):
        """
        Verifica a primeira combinação de slots disponíveis.
        
        Args:
            n (int): Número de slots necessários.
            l (list): Lista de slots disponíveis.
        
        Returns:
            list: Lista de slots alocados.
        """
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
        """
        Verifica a melhor combinação de slots disponíveis.
        
        Args:
            n_slot (int): Número de slots necessários.
            lista (list): Lista de slots disponíveis.
        
        Returns:
            list: Lista de slots alocados.
        """
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