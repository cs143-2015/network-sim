from components import Host
from events import EventTarget
from events.event_types import PacketReceivedEvent


class Link(EventTarget):
    def __init__(self, identifier, rate, delay, buffer_size, node1, node2):
        """
        A network link.

        Args:
            identifier (str):           The name of the link.
            rate (float):               The link capacity, in Mbps.
            delay (int):                The link delay, in ms.
            buffer_size (int):          The buffer size, in KB.
            node1 (Node):               The first endpoint of the link.
            node2 (Node):               The second endpoint of the link.
        """
        super(Link, self).__init__()

        self.id = identifier
        self.rate = rate
        self.delay = delay
        self.buffer_size = buffer_size
        self.node1 = node1
        self.node2 = node2

        self.node1.add_link(self)
        self.node2.add_link(self)

        # This determines whether the link is in use to handle half-duplex
        self.in_use = False

        # The buffer of packets going towards node 1 or node 2
        self.buffer = {
            1: [],
            2: []
        }

    def __len__(self):
        """
        Defines the cost of sending a packet across the link

        :return: Link cost
        :rtype: int
        """
        return self.rate

    def __repr__(self):
        return "Link[%s <=> %s]" % (self.node1, self.node2)

    def other_node(self, ref_node):
        """
        Returns the other node that is not the given reference node

        :param ref_node: Node not to return
        :type ref_node: Node
        :return: Node that is not the given node connected by this link
        :rtype: Node
        """
        assert ref_node is self.node1 or ref_node is self.node2, \
            "Given reference node is not even connected by this link"
        return self.node1 if ref_node is self.node2 else self.node2

    def time_to_send(self, packet):
        packet_size = packet.size()  # in bits
        speed = self.rate / 1.0e6    # in bits/ms
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
            # TODO: do buffer things here
            pass
        else:
            recv_time = time + self.delay
            self.dispatch(PacketReceivedEvent(recv_time, packet, destination))



