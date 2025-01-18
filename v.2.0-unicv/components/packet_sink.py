import simpy

class PacketSink(object):
    """ 
    Recebe os pacotes e coleta informações sobre os atrasos na lista de esperas. 
    Podemos usar essa lista para ver as estatísticas de atraso.
    """
    
    def __init__(self, env, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None):
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
        self.waits = []
        self.arrivals = []
        self.debug = debug
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector
        self.last_arrival = 0.0

    def put(self, pkt):
        """
        Recebe um pacote e coleta estatísticas conforme necessário.

        Args:
            pkt: O pacote a ser recebido.
        """
        # Verifica se o seletor está definido e se o pacote passa pelo seletor (ou se não há seletor)
        if not self.selector or self.selector(pkt):

            # Obtém o tempo atual do ambiente de simulação
            now = self.env.now  

            # Se a gravação de tempos de espera está ativada, adiciona o tempo de espera do pacote à lista
            if self.rec_waits:
                self.waits.append(now - pkt.time)
                
            # Se a gravação de tempos de chegada está ativada
            if self.rec_arrivals:

                # Se as chegadas absolutas estão ativadas, registra o tempo atual
                if self.absolute_arrivals:
                    self.arrivals.append(now)

                # Caso contrário, registra o tempo desde a última chegada
                else:
                    self.arrivals.append(now - self.last_arrival)

                # Atualiza o tempo da última chegada
                self.last_arrival = now  

            # Incrementa o contador de pacotes recebidos    
            self.packets_rec += 1  

            # Incrementa o contador de bytes recebidos com o tamanho do pacote
            # self.bytes_rec += pkt.size

            # Se o modo de depuração está ativado, imprime o pacote
            if self.debug:  
                print(pkt)
