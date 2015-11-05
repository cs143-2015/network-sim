from components.packet import Packet
from events import EventTarget
from events.event_types import PacketSentEvent

class Host(EventTarget):
    def __init__(self, id):
        """
        A network host.

        Args:
            id (str):   The name of the host.
        """
        super(Host, self).__init__()
        self.link = None
        self.id = id

    def receive(self, packet, time):
        """
        Handles receipt of a packet.

        Args:
            packet (Packet):                The packet.
        """
        print "%s received packet %s at time t = %d ms" % (self, packet, time)
        ack_packet = Packet([0 for i in range(Packet.ACK_PACKET_SIZE)], self, packet.src)
        self.dispatch(PacketSentEvent(time, ack_packet, self.link, packet.src))

    def __repr__(self):
        return "Host[%s]" % self.id
