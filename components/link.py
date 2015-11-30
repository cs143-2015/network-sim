from components import Host
from events import EventTarget
from events.event_types import PacketReceivedEvent, LinkFreeEvent
from link_buffer import LinkBuffer
from utils import Logger


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
        self.buffer_size = buffer_size * 1024
        self.node1 = node1
        self.node2 = node2

        self.node1.add_link(self)
        self.node2.add_link(self)

        # This determines whether the link is in use to handle half-duplex
        self.in_use = False
        self.current_dir = None

        # The buffer of packets going towards node 1 or node 2
        self.buffer = LinkBuffer(self)

    def __len__(self):
        """
        Defines the cost of sending a packet across the link
        :return: Link cost
        :rtype: int
        """
        return self.rate

    def __repr__(self):
        return "Link[%s,%s--%s]" % (self.id, self.node1, self.node2)

    def transmission_delay(self, packet):
        packet_size = packet.size() * 8  # in bits
        speed = self.rate * 1e6 / 1e3    # in bits/ms
        return packet_size / float(speed)

    def get_node_by_direction(self, direction):
        if direction == 1:
            return self.node1
        elif direction == 2:
            return self.node2
        return None

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

    def send(self, time, packet, origin):
        """
        Sends a packet to a destination.

        Args:
            packet (Packet):                The packet.
            destination (Host|Router):      The destination of the packet.
            time (int):                     The time at which the packet was
                                            sent.
        """
        destination_id = 2 if origin == self.node1 else 1
        destination = self.node1 if destination_id == 1 else self.node2
        if self.in_use:
            Logger.debug(time, "Link %s in use, currently sending to node %d (trying to send %s)" % (self.id, self.current_dir, packet))
            if self.buffer.size() >= self.buffer_size:
                # Drop packet if buffer is full
                Logger.debug(time, "Buffer full; packet %s dropped." % packet)
                return
            self.buffer.add_to_buffer(packet, destination_id, time)
        else:
            transmission_delay = self.transmission_delay(packet)
            Logger.debug(time, "Link %s free, sending packet %s to %s" % (self.id, packet, destination))
            recv_time = time + transmission_delay + self.delay
            self.dispatch(PacketReceivedEvent(recv_time, packet, destination))
            self.in_use = True
            self.current_dir = destination_id

            # Link will be free to send to same spot once packet has passed
            # through fully, but not to send from the current destination until
            # the packet has completely passed
            self.dispatch(LinkFreeEvent(time + transmission_delay, self, destination_id))
            # (3 - destination_id) is used to quickly get the other node;
            # 3 - 1 = 2, 3 - 2 = 1, so it switches 1 <--> 2.
            self.dispatch(LinkFreeEvent(time + transmission_delay + self.delay, self, 3 - destination_id))
