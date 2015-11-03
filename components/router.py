from events import EventTarget

class Router(EventTarget):
    def __init__(self, id):
        """
        A network router.

        Args:
            id (str):   The name of the router.
        """
        self.id = id

        # { link_id : (static_cost, dynamic_cost) }
        self.links = {}

        # { host_id : link_id }
        self.routing_table = {}

    def receive(self, packet):
        """
        Handles receipt of a packet.

        Args:
            packet (Packet):                The packet.
        """
        pass

    def broadcast(self, packet):
        """
        Broadcasts a packet to all nodes.

        Args:
            packet (Packet):                The packet.
        """
        pass
