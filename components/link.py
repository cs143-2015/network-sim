class Link:
    def __init__(self, id, rate, delay, buffer_size, node1, node2):
        """
        A network link.

        Args:
            id (str):                   The name of the link.
            rate (float):               The link capacity, in Mbps.
            delay (int):                The link delay, in ms.
            buffer_size (int):          The buffer size, in KB.
            destination (Host|Router):  The destination of the link.
            node1 (Host|Router):        The first endpoint of the link.
            node2 (Host|Router):        The second endpoint of the link.
        """
        self.id = id
        self.rate = rate
        self.delay = delay
        self.buffer_size = buffer_size
        self.node1 = node1
        self.node2 = node2
