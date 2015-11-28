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
        if direction == LinkBuffer.NODE_1_ID:
            return self.node1
        elif direction == LinkBuffer.NODE_2_ID:
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
        dst_id = LinkBuffer.NODE_1_ID \
            if destination == self.node1 else LinkBuffer.NODE_2_ID
        if self.in_use:
            Logger.debug(time, "Link in use, currently sending to node %d "
                               "(trying to send %s)" %
                         (self.current_dir, packet))
            if self.buffer.size() >= self.buffer_size:
                # Drop packet if buffer is full
                Logger.debug(time, "Buffer full; packet %s dropped." % packet)
                return
            self.buffer.add_to_buffer(packet, dst_id, time)
        else:
            transmission_delay = self.transmission_delay(packet)
            Logger.debug(time, "Link free, sending packet %s" % packet)
            recv_time = time + transmission_delay + self.delay
            self.dispatch(PacketReceivedEvent(recv_time, packet, destination))
            self.in_use = True
            self.current_dir = dst_id

            # Link will be free to send to same spot once packet has passed
            # through fully, but not to send from the current destination until
            # the packet has completely passed
            self.dispatch(LinkFreeEvent(time + transmission_delay, self, dst_id))
            self.dispatch(LinkFreeEvent(time + transmission_delay + self.delay, self, self.get_other_id(dst_id)))

    @classmethod
    def get_other_id(cls, dest_id):
        """
        Get the node id of the other node that is not the given destination id.

        :param dest_id: Destination ID
        :type dest_id: int
        :return: ID of the node that is not the destination ID
        :rtype:
        """
        return LinkBuffer.NODE_1_ID \
            if dest_id == LinkBuffer.NODE_2_ID else LinkBuffer.NODE_1_ID
