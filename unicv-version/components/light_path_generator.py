import random
from components.light_path_request import LightPathRequest

class LightPathGenerator(object):
    """ Gera pacotes com uma distribuição de tempo de chegada dada.
        Estabelece a variável membro "out" à entidade que receberá o pacote.
    """

    def __init__(self, env, id, avegLightpathDuration, load, numberNodes=5, num_max_pet=10, num_max_slots=3):
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
        """
        self.env = env
        self.id = id
        self.avegLightpathDuration = avegLightpathDuration
        self.timeBetweenReq = avegLightpathDuration / (load * (numberNodes - 1))
        self.numberNodes = numberNodes
        self.load = load
        self.out = None
        self.num_max_pet = num_max_pet
        self.num_max_slots = num_max_slots
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
            destino = list(range(1, self.numberNodes + 1))  # Ajustado para começar em 1

            # Verifica se o próprio ID está na lista de destinos possíveis e o remove para evitar auto-envio
            if self.id in destino:
                destino.remove(self.id)

            # Escolhe aleatoriamente um destino da lista atualizada de destinos possíveis
            dst = random.choice(destino)

            # Gera um número aleatório de slots para o pedido, dentro do limite máximo definido
            nslots = random.randint(1, self.num_max_slots)

            # Obtém o tempo atual do ambiente de simulação para marcar o início do pedido
            now = self.env.now

            # Cria um novo LightPathRequest
            p = LightPathRequest(PKT_SENTS, self.id, dst, now, duration, nslots)

            # Estabelece a variável membro "out" à entidade que receberá o pacote
            self.out.put(p)

            # Incrementa o contador de pacotes enviados
            PKT_SENTS += 1
            
        # Sinaliza o fim dos pedidos gerados por essa classe
        self.out.put(None)
