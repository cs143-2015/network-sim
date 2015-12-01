from components.packet_types import AckPacket, Packet, RoutingPacket, FlowPacket
from events.event_types import PacketSentToLinkEvent, TimeoutEvent, AckReceivedEvent, \
                               FlowPacketReceivedEvent, FlowStartEvent, \
                               WindowSizeEvent
from errors import UnhandledPacketType
from utils import Logger
from node import Node


class CongestionControl:
    NONE = 0
    TAHOE = 1
    RENO = 2


class Host(Node):
    INITIAL_CWND = 2
    INITIAL_SSTHRESH = 1e6
    SEQ_MAX = 1e6
    TIMEOUT_TOLERANCE = 1000

    def __init__(self, identifier):
        """
        A network host.

        Args:
            identifier (str):   The name of the host.
        """
        super(Host, self).__init__(identifier)
        self.link = None
        self.flows = {}
        # Congestion window sizes per flow. { flow_id : cwnd }
        self.cwnd = {}
        # Whether a given flow is in slow start or not. { flow_id : is_SS }
        self.ss = {}
        # Self Start thresholds
        self.ssthresh = {}
        # Sequence Number / Base / Maximum for each flow
        self.sequence_nums = {}
        # Current request number for flow, held by SENDER
        self.current_request_num = {}
        # Request Number for each flow, held by RECEIVER
        self.request_nums = {}
        # Last drop per flow
        self.last_drop = {}

        self.awaiting_ack = {}
        self.queue = set()

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
        assert self.link is None, "Hosts can only have one link attached."
        self.link = link

    def add_flow(self, flow_id, destination, amount, start,
                 congestion_method=CongestionControl.NONE):
        byte_amount = int(amount * 1024 * 1024)
        self.flows[flow_id] = (destination, byte_amount, start, congestion_method)
        self.cwnd[flow_id] = Host.INITIAL_CWND
        self.ss[flow_id] = True
        self.ssthresh[flow_id] = Host.INITIAL_SSTHRESH
        self.sequence_nums[flow_id] = (0, 0, Host.SEQ_MAX)
        self.last_drop[flow_id] = None

    def set_window_size(self, time, flow_id, value):
        Logger.info(time, "Window size changed from %0.2f -> %0.2f for flow %s" % (self.cwnd[flow_id], value, flow_id))
        self.cwnd[flow_id] = value
        self.dispatch(WindowSizeEvent(time, flow_id, self.cwnd[flow_id]))

    def start_flows(self):
        for flow_id, (destination, amount, start, congestion_method) in self.flows.items():
            time = start * 1000.
            self.dispatch(FlowStartEvent(time, self, flow_id))
            self.dispatch(WindowSizeEvent(time, flow_id, self.cwnd[flow_id]))

    def send_packets(self, time, flow_id):
        destination, flow_amount, start, congestion_method = self.flows[flow_id]
        # We want to fill up our window
        while len(self.awaiting_ack) < self.cwnd[flow_id]:
            # If there is nothing being retransmitted, add new flow packets
            if len(self.queue) == 0:
                Sn, Sb, Sm = self.sequence_nums[flow_id]
                if not (Sb <= Sn <= Sm):
                    break

                total_sent = Sn * FlowPacket.FLOW_PACKET_SIZE
                if total_sent >= flow_amount:
                    return
                if total_sent + FlowPacket.FLOW_PACKET_SIZE >= flow_amount:
                    size = flow_amount - total_sent
                else:
                    size = FlowPacket.FLOW_PACKET_SIZE

                packet = FlowPacket(flow_id, Sn, size, self, destination)

                Sn += 1
                self.sequence_nums[flow_id] = (Sn, Sb, Sm)

                if packet.id in self.awaiting_ack or \
                   packet.sequence_number < self.current_request_num.get(flow_id, 0):
                    # We already sent it out
                    continue

                self.send(packet, time)
            else:
                # We need to retransmit packets
                to_send = sorted(self.queue, key=lambda p: p.sequence_number)[0]
                self.queue.remove(to_send)
                self.send(to_send, time)

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
        self.dispatch(PacketSentToLinkEvent(time, self, packet, self.link))
        # Still awaiting Ack on receipt of this package
        self.awaiting_ack[packet.id] = packet
        if isinstance(packet, FlowPacket):
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
            flow_id = packet.flow_id
            Rn = packet.request_number

            if flow_id not in self.current_request_num:
                self.current_request_num[flow_id] = Rn
            else:
                self.current_request_num[flow_id] = max(Rn, self.current_request_num[flow_id])

            # Receiving request number Rn means every packet with sequence
            # number <= Rn - 1 was received, so those have been acked. No need
            # to wait for their ack or to resend.
            acked_packets = []
            for packet_id, packet in self.awaiting_ack.items():
                if packet.sequence_number < Rn:
                    acked_packets.append(packet_id)
            for acked_packet_id in acked_packets:
                packet = self.awaiting_ack[acked_packet_id]
                if packet in self.queue:
                    self.queue.remove(packet)
                del self.awaiting_ack[acked_packet_id]

            if self.ss[flow_id]:
                self.set_window_size(time, flow_id, self.cwnd[flow_id] + 1)
                if self.cwnd[flow_id] >= self.ssthresh[flow_id]:
                    self.ss[flow_id] = False
                    Logger.info(time, "SS phase over for Flow %s. CA started." % (flow_id))

            Sn, Sb, Sm = self.sequence_nums[flow_id]
            if Rn > Sb:
                if not self.ss[flow_id]:
                    # If we are in Congestion Avoidance mode, we wait for an RTT to
                    # increase the window size, rather than doing it on ACK.
                    self.set_window_size(time, flow_id, self.cwnd[flow_id] + 1. / self.cwnd[flow_id])
                Sm = Sm + (Rn - Sb)
                Sb = Rn
                Sn = Sb
                self.send_packets(time, flow_id)
            self.sequence_nums[flow_id] = (Sn, Sb, Sm)

        elif isinstance(packet, RoutingPacket):
            return
        # Regular packet, send acknowledgment of receipt
        elif isinstance(packet, FlowPacket):
            if packet.flow_id not in self.request_nums:
                self.request_nums[packet.flow_id] = 0
            if packet.sequence_number == self.request_nums[packet.flow_id]:
                Logger.warning(time, "Packet %d accepted from %s" % (packet.sequence_number, packet.src))
                self.request_nums[packet.flow_id] += 1
            else:
                Logger.info(time, "Incorrect packet received from %s. Expected %d, got %d." % (packet.src, self.request_nums[packet.flow_id], packet.sequence_number))
            ack_packet = AckPacket(packet.flow_id, self, packet.src, self.request_nums[packet.flow_id])
            self.send(ack_packet, time)
        # Ignore routing packets
        else:
            raise UnhandledPacketType

    def timeout(self, time, packet):
        """
        A timeout occurred at the given time on the given packet. Resend if
        necessary.

        :param time: Time to resend the packet
        :type time: int
        :param packet: Packet which timed out
        :type packet: Packet
        """
        # We already received an Ack for it
        if packet.id not in self.awaiting_ack:
            return
        else:
            # Otherwise, remove it so that it will be added again
            del self.awaiting_ack[packet.id]

        if not isinstance(packet, FlowPacket):
            # If an ACK packet is dropped, don't worry about it, it'll be sent
            # again later
            return
        flow_id = packet.flow_id
        if packet.sequence_number < self.current_request_num[flow_id]:
            # Packet was already received
            return

        if self.last_drop[flow_id] is None or \
           time - self.last_drop[flow_id] > Host.TIMEOUT_TOLERANCE:
            self.ss[flow_id] = True
            self.ssthresh[flow_id] = max(self.cwnd[flow_id] / 2, Host.INITIAL_CWND)
            self.set_window_size(time, flow_id, Host.INITIAL_CWND)

            self.last_drop[flow_id] = time

            Logger.warning(time, "Timeout Received. SS_Threshold -> %d" % self.ssthresh[flow_id])

        # Resend
        Logger.info(time, "Packet %s was dropped, resending" % (packet.id))
        self.queue.add(packet)
        self.send_packets(time, flow_id)
