class LightPathRequest(object):
    """ 
    Classe que representa uma requisição de lightpath.
    Encapsula os detalhes de uma solicitação para estabelecer um caminho óptico entre dois nós na rede.
    """

    def __init__(self, id, src, dst, time, duration=0, nslots=0, flow_id=0):
        """
        Inicializa a instância de LightPathRequest com os parâmetros fornecidos

        Args:
            id: Identificador único para a requisição de lightpath
            src: Nó de origem da requisição
            dst: Nó de destino da requisição
            time: Tempo de início da requisição
            duration: Duração da requisição em segundos (valor padrão é 0)
            nslots: Número de slots espectrais necessários para a requisição (valor padrão é 0)
            flow_id: Identificador do fluxo ao qual a requisição pertence (valor padrão é 0)
        """
        self.id = id
        self.src = src
        self.dst = dst
        self.time = time
        self.duration = duration
        self.nslots = nslots
        self.fim = self.time + self.duration    # Calcula o tempo de término da requisição
        self.flow_id = flow_id

    def __repr__(self):
        """
        Retorna uma representação em string da instância, útil para depuração e logging
        """

        return "[{}s] \t #{} \t nodo {} ==> nodo {} \t nslots={} \t d={}s \t f={}s \t flow_id={}". format(round(self.time, 2), self.id, self.src, self.dst, self.nslots, round(self.duration, 2), round(self.fim, 2), self.flow_id)