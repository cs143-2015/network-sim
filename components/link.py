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
            node1 (Host|Router):        The first endpoint of the link.
            node2 (Host|Router):        The second endpoint of the link.
        """
        super(Link, self).__init__()

        self.id = identifier
        self.rate = rate
        self.delay = delay
        self.buffer_size = buffer_size * 1024
        self.node1 = node1
        self.node2 = node2

        self.node1.link = self
        self.node2.link = self

        # This determines whether the link is in use to handle half-duplex
        self.in_use = False
        self.current_dir = None

        # The buffer of packets going towards node 1 or node 2
        self.buffer = LinkBuffer(self)

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

    def send(self, packet, destination, time):
        """
        Sends a packet to a destination.

        Args:
            packet (Packet):                The packet.
            destination (Host|Router):      The destination of the packet.
            time (int):                     The time at which the packet was
                                            sent.
        """
        destination_id = 1 if destination == self.node1 else 2
        if self.in_use:
            Logger.debug(time, "Link in use, currently sending to node %d" % self.current_dir)
            if self.buffer.size() >= self.buffer_size:
                # Drop packet if buffer is full
                Logger.debug(time, "Buffer full; packet %s dropped." % packet)
                return
            self.buffer.add_to_buffer(packet, destination_id)
        else:
            transmission_delay = self.transmission_delay(packet)
            Logger.info(time, "Link free, sending packet %s" % packet)
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

    def __repr__(self):
        return "Link[%s,%s--%s]" % (self.id, self.node1, self.node2)

