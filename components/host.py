from events import EventTarget

class Host(EventTarget):
    def __init__(self, id):
        """
        A network host.

        Args:
            id (str):   The name of the host.
        """
        self.id = id

    def receive(self, packet):
        """
        Handles receipt of a packet.

        Args:
            packet (Packet):                The packet.
        """
        pass
