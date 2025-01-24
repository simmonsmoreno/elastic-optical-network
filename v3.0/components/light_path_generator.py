import random
import simpy
from components.light_path_request import LightPathRequest
from components.packet_sink import PacketSink
from typing import Optional

class LightPathGenerator:
    """ 
    Gera pacotes com uma distribuição de tempo de chegada dada.
    Estabelece a variável membro "out" à entidade que receberá o pacote.
    """

    def __init__(self, env: simpy.Environment, id: int, avegLightpathDuration: float, load: float, numberNodes: int = 5, num_max_pet: int = 10, num_max_slots: int = 3, node_range: Optional[range] = None):
        """
        Inicializa o gerador de lightpaths.

        Args:
            env: O ambiente de simulação do SimPy.
            id: Identificador do nó.
            avegLightpathDuration: Duração média do lightpath.
            load: Carga da rede.
            numberNodes: Número de nós na rede.
            num_max_pet: Número máximo de pedidos.
            num_max_slots: Número máximo de slots.
            node_range: Intervalo de nós permitidos.
        """
        self.env = env
        self.id = id
        self.avegLightpathDuration = avegLightpathDuration
        self.timeBetweenReq = avegLightpathDuration / (load * (numberNodes - 1))
        self.numberNodes = numberNodes
        self.load = load
        self.out: Optional[PacketSink] = None
        self.num_max_pet = num_max_pet
        self.num_max_slots = num_max_slots
        self.node_range = node_range if node_range else range(numberNodes)
        self.flow_id = 0
        self.action = env.process(self.run())

    def run(self):
        """
        A função geradora utilizada nas simulações. Gera pedidos de lightpaths com base em distribuições exponenciais.
        """
        global PKT_SENTS
        PKT_SENTS = 0

        while PKT_SENTS < self.num_max_pet:
            # Espera pela próxima transmissão
            duration = random.expovariate(1.0 / self.avegLightpathDuration)

            # O tempo entre pedidos feitos por cada fonte é calculado de forma aleatória com uma variável de tipo exponencial com média
            yield self.env.timeout(random.expovariate(1.0 / self.timeBetweenReq))

            # O nodo de destino do pedido do lightpath é gerado aleatoriamente entre os restantes destinos
            destino = list(self.node_range)

            # Verifica se o próprio ID está na lista de destinos possíveis e o remove para evitar auto-envio
            if self.id in destino:
                destino.remove(self.id)

            # Escolhe aleatoriamente um destino da lista atualizada de destinos possíveis
            dst = random.choice(destino)

            # Gera um número aleatório de slots para o pedido, dentro do limite máximo definido
            nslots = random.randint(1, self.num_max_slots)

            # Obtém o tempo atual do ambiente de simulação para marcar o início do pedido
            now = self.env.now

            # Tamanho do pacote entre 1 e 1000 unidades
            packet_size = random.randint(1, 1000)  

            # Cria um novo LightPathRequest
            p = LightPathRequest(PKT_SENTS, self.id, dst, now, duration, nslots, size=packet_size)

            # Estabelece a variável membro "out" à entidade que receberá o pacote
            if self.out:
                self.out.put(p)

            # Incrementa o contador de pacotes enviados
            PKT_SENTS += 1

        # Sinaliza o fim dos pedidos gerados por essa classe
        if self.out:
            self.out.put(None)