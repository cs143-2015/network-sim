from math import ceil

from packet_types import FlowPacket, AckPacket
from events import EventTarget
from events.event_types import WindowSizeEvent, PacketSentEvent
from utils import Logger

class Flow(EventTarget):
    def __init__(self, id, src, dest, amount, start_time):
        """
        A network flow.

        Args:
            id (str):       The name of the flow.
            src (Host):     The source host.
            dest (Host):    The destination host.
            amount (int):   The amount of data to send, in MB.
            start_time (float):  The time at which the flow starts, in s.
        """
        super(Flow, self).__init__()
        self.id = id
        self.src = src
        self.dest = dest
        self.amount = int(amount * 1024 * 1024)
        self.start_time = start_time * 1000
        self.total_packets = int(ceil(self.amount / FlowPacket.FLOW_PACKET_SIZE))

        # To send/receive packets and ensure they come in the right order, we
        # use Go-Back-N ARQ.
        #
        # For the purposes of TCP congestion avoidance, we use TCP Tahoe.
        self.window_size = 2
        self.request_number = 0
        self.sequence_base = 0
        self.sequence_number = 0
        self.sequence_max = self.window_size - 1

        self.slow_start = False
        self.ss_thresh = 20
        self.in_retransmission = False

    def start(self):
        self.slow_start = True
        Logger.info(self.start_time, "%s sending %d packets." % (self, self.total_packets))
        self.send_packet()
        self.dispatch(WindowSizeEvent(self.start_time, self.id, self.window_size))

    def set_window_size(self, time, value):
        Logger.info(time, "Window size changed from %0.1f -> %0.1f for flow %s" % (self.window_size, value, self.id))
        self.window_size = value
        self.dispatch(WindowSizeEvent(time, self.id, self.window_size))

    def send_packet(self, time=None):
        if not self.slow_start:
            # If we are in Congestion Avoidance mode, we wait for an RTT to
            # increase the window size, rather than doing it on ACK.
            self.set_window_size(time, self.window_size + 1)
        if time == None:
            time = self.start_time
        if len(self.src.retransmitting) == 0:
            n = 0
            while n < self.window_size:
                # If no packet is being retransmitted, we are free to send a packet
                # with sequence number Sb <= Sn <= Sm, where we are transmitting in
                # order.
                total_sent = self.sequence_number * FlowPacket.FLOW_PACKET_SIZE
                if total_sent > self.amount:
                    return
                if total_sent + FlowPacket.FLOW_PACKET_SIZE >= self.amount:
                    size = self.amount - total_sent
                else:
                    size = FlowPacket.FLOW_PACKET_SIZE
                packet = FlowPacket(self, self.sequence_number, size, self.src, self.dest)
                self.src.send(packet, time)

                self.sequence_number += 1
                n += 1

    def timeout_received(self, time):
        self.slow_start = False
        self.ss_thresh = max(self.window_size / 2, 1)
        self.set_window_size(time, 1)
        Logger.info(time, "Timeout Received. SS_Threshold -> %d" % self.ss_thresh)

    def __repr__(self):
        units = "B"
        amount_sending = self.amount # this is in B
        if amount_sending >= 1024:
            amount_sending /= 1024.0
            units = "KB"
        if amount_sending >= 1024:
            amount_sending /= 1024.0
            units = "MB"

        return 'Flow[%s: %s -(%d%s)-> %s]' % (self.id, self.src,
                                              amount_sending, units,
                                              self.dest)
