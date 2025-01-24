class LightPathRequest:
    """ 
    Class representing a lightpath request.
    Encapsulates the details of a request to establish an optical path between two nodes in the network.
    """

    def __init__(self, id: int, src: int, dst: int, time: float, duration: float = 0, nslots: int = 0, flow_id: int = 0, size: int = 100):
        """
        Initializes the LightPathRequest instance with the provided parameters.

        Args:
            id (int): Unique identifier for the lightpath request
            src (int): Source node of the request
            dst (int): Destination node of the request
            time (float): Start time of the request
            duration (float): Duration of the request in seconds (default is 0)
            nslots (int): Number of spectral slots required for the request (default is 0)
            flow_id (int): Identifier of the flow to which the request belongs (default is 0)
            size (int): Size of the packet associated with the request (default is 100)
        """
        self.id = id
        self.src = src
        self.dst = dst
        self.time = time
        self.duration = duration
        self.nslots = nslots
        self.fim = self.time + self.duration  # Calculate the end time of the request
        self.flow_id = flow_id
        self.size = size

    def __repr__(self) -> str:
        """
        Returns a string representation of the instance, useful for debugging and logging.
        """
        return (f"\t #{self.id} \t node {self.src} ==> node {self.dst} \t no_slots={self.nslots} "
                f"\t duration={round(self.duration, 2)}sec \t end_time={round(self.fim, 2)}sec "
                f"\t flow_id={self.flow_id} \t size={self.size}")