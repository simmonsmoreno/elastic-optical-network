class LightPathRequest:
    """ 
    Classe que representa uma solicitação de caminho óptico.
    Envolve os detalhes de uma solicitação para estabelecer um caminho óptico entre dois nós na rede.
    """

    def __init__(self, id: int, src: int, dst: int, time: float, duration: float = 0, nslots: int = 0, flow_id: int = 0, size: int = 100):
        """
        Inicializa a instância de LightPathRequest com os parâmetros fornecidos.

        Args:
            id (int): Identificador único para a solicitação de caminho óptico
            src (int): Nó de origem da solicitação
            dst (int): Nó de destino da solicitação
            time (float): Hora de início da solicitação
            duration (float): Duração da solicitação em segundos (o padrão é 0)
            nslots (int): Número de slots espectrais necessários para a solicitação (o padrão é 0)
            flow_id (int): Identificador do fluxo ao qual a solicitação pertence (o padrão é 0)
            size (int): Tamanho do pacote associado à solicitação (o padrão é 100)
        """
        self.id = id
        self.src = src
        self.dst = dst
        self.time = time
        self.duration = duration
        self.nslots = nslots
        self.fim = self.time + self.duration  # Calcula o tempo de término da solicitação
        self.flow_id = flow_id
        self.size = size

    def __repr__(self) -> str:
        """
        Retorna uma representação em string da instância, útil para depuração e registro.
        """
        return (f"\t #{self.id} \t nó {self.src} ==> nó {self.dst} \t no_slots={self.nslots} "
                f"\t duração={round(self.duration, 2)}seg \t tempo_fim={round(self.fim, 2)}seg "
                f"\t flow_id={self.flow_id} \t tamanho={self.size}")