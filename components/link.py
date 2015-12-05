from components import Host
from events import EventTarget
from events.event_types import PacketSentOverLinkEvent, LinkFreeEvent
from events.event_types.graph_events import DroppedPacketEvent, LinkThroughputEvent
from link_buffer import LinkBuffer
from utils import Logger


class Link(EventTarget):
    def __init__(self, identifier, rate, delay, buffer_size, node1, node2):
        """
        A network link.

        Args:
            identifier (str):           The name of the link.
            rate (float):               The link capacity, in Mbps.
            delay (int):                Propagation delay, in ms.
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

        # True if one node requested a reset of avg. buffer time
        self.avgBufferTimeReset = False

        # The buffer of packets going towards node 1 or node 2
        self.buffer = LinkBuffer(self)

        # Bytes sent over this link
        self.bytesSent = 0.0
        # Time it has taken so far to send these bytes
        self.sendTime = 0.0

    def __repr__(self):
        return "Link[%s,%s--%s]" % (self.id, self.node1, self.node2)

    def static_cost(self):
        """
        Defines the static cost of sending a packet across the link

        :return: Static link cost
        :rtype: float
        """
        return self.rate

    def dynamic_cost(self):
        """
        Defines the dynamic cost of sending a packet across the link

        :return: Dynamic link cost
        :rtype: float
        """
        return self.static_cost() + self.buffer.avg_buffer_time

    def reset_average_buffer_time(self, node, time):
        """
        Resets the average buffer times for all the buffers

        :param node: Node resetting the average buffer time
        :type node: Node
        :param time: Time when the reset is happening
        :type time: float
        :return: Nothing
        :rtype: None
        """
        # If the other node has requested a reset of the average buffer time,
        # or if the other node if the host (will not use the average buffer
        # time or call for a reset), then reset it
        if self.avgBufferTimeReset or isinstance(self.other_node(node), Host):
            self.buffer.reset_buffer_time(time)
        else:
            Logger.debug(time, "Avg. buffer time reset request by %s" % node)
            self.avgBufferTimeReset = True

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

    def send(self, time, packet, origin):
        """
        Sends a packet to a destination.

        Args:
            time (int):                The time at which the packet was sent.
            packet (Packet):           The packet.
            origin (Host|Router):      The node origin of the packet.
        """
        dst_id = LinkBuffer.NODE_2_ID \
            if origin == self.node1 else LinkBuffer.NODE_1_ID
        destination = self.node1 \
            if dst_id == LinkBuffer.NODE_1_ID else self.node2
        if self.in_use:
            Logger.debug(time, "Link %s in use, currently sending to node %d "
                               "(trying to send %s)"
                               % (self.id, self.current_dir, packet))
            # Drop packet if buffer is full
            if self.buffer.size() + packet.size() > self.buffer_size:
                Logger.debug(time, "Buffer full; packet %s dropped." % packet)
                self.dispatch(DroppedPacketEvent(time, self.id))
                return
            self.buffer.add_to_buffer(packet, dst_id, time)
        else:
            Logger.debug(time, "Link %s free, sending packet %s to %s" % (self.id, packet, destination))
            self.in_use = True
            self.current_dir = dst_id
            transmission_delay = self.transmission_delay(packet)

            self.dispatch(PacketSentOverLinkEvent(time, packet, destination, self))
            self.in_use = True
            self.current_dir = dst_id

            # Link will be free to send to same spot once packet has passed
            # through fully, but not to send from the current destination until
            # the packet has completely passed.
            # Transmission delay is delay to put a packet onto the link
            self.dispatch(LinkFreeEvent(time + transmission_delay, self, dst_id))
            self.dispatch(LinkFreeEvent(time + transmission_delay + self.delay, self, self.get_other_id(dst_id)))
            self.update_link_throughput(time, packet,
                                        time + transmission_delay + self.delay)

    def update_link_throughput(self, time, packet, time_received):
        """
        Update the link throughput

        :param time: Time when this update is occurring
        :type time: float
        :param packet: Packet we're updating the throughput with
        :type packet: Packet
        :param time_received: Time the packet was received at the other node
        :type time_received: float
        :return: Nothing
        :rtype: None
        """
        self.bytesSent += packet.size()
        self.sendTime = time_received
        assert self.sendTime != 0, "Packet should not be received at time 0."
        throughput = (8 * self.bytesSent) / (self.sendTime / 1000)  # bits/s
        Logger.debug(time, "%s throughput is %f" % (self, throughput))
        self.dispatch(LinkThroughputEvent(time, self.id, throughput))

    @classmethod
    def get_other_id(cls, dst_id):
        """
        Get the node id of the other node that is not the given destination id.

        :param dst_id: Destination ID
        :type dst_id: int
        :return: ID of the node that is not the destination ID
        :rtype:
        """
        return LinkBuffer.NODE_1_ID \
            if dst_id == LinkBuffer.NODE_2_ID else LinkBuffer.NODE_2_ID
