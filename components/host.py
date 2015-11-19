from components.packet_types import AckPacket, Packet, RoutingPacket, FlowPacket
from events.event_types import PacketSentEvent, TimeoutEvent, AckReceivedEvent, \
                               FlowPacketReceivedEvent
from errors import UnhandledPacketType
from utils import Logger
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
        self.retransmitting = set()

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
        Logger.info(time, "%s sent packet %s." % (self, packet))
        # Send the packet
        self.dispatch(PacketSentEvent(time, packet, self.link, packet.dest))
        # Still awaiting Ack on receipt of this package
        self.awaiting_ack[packet.id] = packet
        # Dispatch an event to resend the package if we haven't received an
        # Ack by the timeout period
        timeout_time = time + TimeoutEvent.TIMEOUT_PERIOD
        self.dispatch(TimeoutEvent(timeout_time, self, packet))

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
        Logger.info(time, "%s received packet %s." % (self, packet))
        # Ack packet, drop stored data that might need retransmission
        if isinstance(packet, AckPacket):
            packet_id = "".join(packet.payload)
            flow_id, request_number_str = packet_id.split(".")
            request_number = int(request_number_str)

            original_packet_id = "%s.%d" % (flow_id, request_number - 1)

            if original_packet_id in self.awaiting_ack:
                del self.awaiting_ack[original_packet_id]
            self.dispatch(AckReceivedEvent(time, self, packet.flow))

        elif isinstance(packet, RoutingPacket):
            return
        # Regular packet, send acknowledgment of receipt
        elif isinstance(packet, FlowPacket):
            self.dispatch(FlowPacketReceivedEvent(time, packet, packet.flow))
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
        :return: Whether we needed to resend or not
        :rtype: bool
        """
        # We received an Ack, no need to resend
        if packet_id not in self.awaiting_ack:
            return False
        # Resend
        Logger.info(time, "Packet %s was dropped, resending" % (packet_id))
        packet = self.awaiting_ack.pop(packet_id)
        self.send(packet, time)
        self.retransmitting.add(packet)
        return True
