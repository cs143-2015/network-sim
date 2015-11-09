from components.packet_types import AckPacket, Packet, RoutingPacket
from events.event_types import PacketSentEvent, TimeoutEvent
from errors import UnhandledPacketType
from node import Node


class Host(Node):
    def __init__(self, identifier):
        """
        A network host.

        Args:
            identifier (str):   The name of the host.
        """
        super(Host, self).__init__(identifier)
        self.link = None
        self.awaiting_ack = {}

    def __repr__(self):
        return "Host[%s]" % self.id

    def add_link(self, link):
        """
        Sets the Host's only link

        :param link: Link to add
        :type link: Link
        :return: Nothing
        :rtype: None
        """
        self.link = link

    def send(self, packet, time):
        """
        Handles sending a packet

        :param packet: Packet to send
        :type packet: Packet
        :param time: Time to send the packet
        :type time: int
        :return: Nothing
        :rtype: None
        """
        assert self.link, "Can't send anything when link hasn't been connected"
        # Send the packet
        self.dispatch(PacketSentEvent(time, packet, self.link, packet.dest))
        # Still awaiting Ack on receipt of this package
        self.awaiting_ack[packet.id] = packet
        # Dispatch an event to resend the package if we haven't received an
        # Ack by the timeout period
        timeout_time = time + TimeoutEvent.TIMEOUT_PERIOD
        self.dispatch(TimeoutEvent(timeout_time, self, packet.id))

    def receive(self, packet, time):
        """
        Handles receipt of a packet.

        :param packet: Packet received
        :type packet: Packet | AckPacket
        :param time: Time the packet was received
        :type time: int
        :return: Nothing
        :rtype: None
        """
        print "%s received packet %s at time t = %d ms" % (self, packet, time)
        # Ack packet, drop stored data that might need retransmission
        if isinstance(packet, AckPacket):
            ack_packet = self.awaiting_ack.pop("".join(packet.payload), None)
            assert ack_packet, "Double acknowledgement received"
        elif isinstance(packet, RoutingPacket):
            return
        # Regular packet, send acknowledgment of receipt
        elif isinstance(packet, Packet):
            ack = AckPacket(packet.id, self, packet.src)
            self.dispatch(PacketSentEvent(time, ack, self.link, packet.src))
        # Ignore routing packets
        else:
            raise UnhandledPacketType

    def resend_if_necessary(self, packet_id, time):
        """
        Resend the packet with the given packet ID

        :param packet_id: Packet ID of the packet to resend
        :type packet_id: int
        :param time: Time to resend the packet
        :type time: int
        :return: Nothing
        :rtype: None
        """
        # We received an Ack, no need to resend
        if packet_id not in self.awaiting_ack:
            return
        # Resend
        print "Packet %s was dropped; resending (t = %f)" % (packet_id, time)
        self.send(self.awaiting_ack.pop(packet_id), time)
