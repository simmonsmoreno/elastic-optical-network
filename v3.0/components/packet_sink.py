import simpy
from typing import List, Optional, Callable
import time

class Packet:
    def __init__(self, time: float, size: int):
        self.time = time
        self.size = size

class PacketSink:
    """ 
    Recebe os pacotes e coleta informações sobre os atrasos na lista de esperas. 
    Podemos usar essa lista para ver as estatísticas de atraso.
    """
    
    def __init__(self, env: simpy.Environment, rec_arrivals: bool = False, absolute_arrivals: bool = False, rec_waits: bool = True, debug: bool = False, selector: Optional[Callable[[Packet], bool]] = None):
        """
        Inicializa a instância de PacketSink com os parâmetros fornecidos.

        Args:
            env: O ambiente de simulação do SimPy.
            rec_arrivals: Se verdadeiro, registrará as chegadas.
            absolute_arrivals: Se verdadeiro, registrará os tempos de chegada absolutos, caso contrário, registrará o tempo entre chegadas consecutivas.
            rec_waits: Se verdadeiro, registrará o tempo de espera experimentado por cada pacote.
            debug: Se verdadeiro, imprimirá o conteúdo de cada pacote conforme recebido.
            selector: Função para seleção de pacotes usado para estatísticas seletivas. Por padrão, nenhum.
        """
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits: List[float] = []
        self.arrivals: List[float] = []
        self.debug = debug
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector
        self.last_arrival = 0.0
        self.start_time = time.time()

    def put(self, pkt: Packet) -> simpy.events.Event:
        """
        Recebe um pacote e coleta estatísticas conforme necessário.

        Args:
            pkt: O pacote a ser recebido.
        """
        if (not self.selector or self.selector(pkt)) and pkt:
            now = self.env.now

            # Sincronizar com o tempo real
            elapsed_sim_time = now
            elapsed_real_time = time.time() - self.start_time
            if elapsed_real_time < elapsed_sim_time:
                time.sleep(elapsed_sim_time - elapsed_real_time)

            if self.rec_waits:
                self.waits.append(now - pkt.time)

            if self.rec_arrivals:
                if self.absolute_arrivals:
                    self.arrivals.append(now)
                else:
                    self.arrivals.append(now - self.last_arrival)
                self.last_arrival = now

            self.packets_rec += 1
            if hasattr(pkt, 'size'):
                self.bytes_rec += pkt.size

            if self.debug:
                print(f"[{now:.2f}s] Pacote recebido: {pkt}")

        return self.store.put(pkt)