from events import EventTarget
from events.event_types import PacketReceivedEvent

class Link(EventTarget):
    def __init__(self, id, rate, delay, buffer_size, node1, node2):
        """
        A network link.

        Args:
            id (str):                   The name of the link.
            rate (float):               The link capacity, in Mbps.
            delay (int):                The link delay, in ms.
            buffer_size (int):          The buffer size, in KB.
            node1 (Host|Router):        The first endpoint of the link.
            node2 (Host|Router):        The second endpoint of the link.
        """
        super(Link, self).__init__()

        self.id = id
        self.rate = rate
        self.delay = delay
        self.buffer_size = buffer_size
        self.node1 = node1
        self.node2 = node2

        self.node1.link = self
        self.node2.link = self

        # This determines whether the link is in use to handle half-duplex
        self.in_use = False

        # The buffer of packets going towards node 1 or node 2
        self.buffer = {
            1: [],
            2: []
        }

    def time_to_send(self, packet):
        packet_size = packet.size() # in bits
        speed = self.rate / 1.0e6 # in bits/ms
        return packet_size / speed

    def send(self, packet, destination, time):
        """
        Sends a packet to a destination.

        Args:
            packet (Packet):                The packet.
            destination (Host|Router):      The destination of the packet.
            time (int):                     The time at which the packet was
                                            sent.
        """
        if self.in_use:
            # do buffer things here
            pass
        else:
            recv_time = time + self.delay
            evt = PacketReceivedEvent(packet, destination, recv_time)
            self.dispatch(evt)



