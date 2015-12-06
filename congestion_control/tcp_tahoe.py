from utils import Logger
from protocol import Protocol
from components.packet_types import AckPacket, Packet, RoutingPacket, FlowPacket

class TCPTahoe(Protocol):
    INITIAL_CWND = 2
    INITIAL_SSTHRESH = 1e10
    TIMEOUT_TOLERANCE = 1000

    def __init__(self, host):
        super(TCPTahoe, self).__init__(host)

        # Whether the flow is in slow start or not.
        self.ss = True
        # Self Start threshold
        self.ssthresh = TCPTahoe.INITIAL_SSTHRESH
        # Last drop
        self.last_drop = None

    def handle_send(self, packet, time):
        pass

    def handle_receive(self, packet, time):
        if isinstance(packet, AckPacket):
            Rn = packet.request_number
            Sn, Sb, Sm = self.host.sequence_nums
            cwnd = self.host.cwnd
            if self.ss:
                self.set_window_size(time, cwnd + 1)
                if self.host.cwnd >= self.ssthresh:
                    self.ss = False
                    Logger.info(time, "SS phase over for Flow %s. CA started." % (self.host.flow[0]))
            elif Rn > Sb:
                # If we are in Congestion Avoidance mode, we wait for an RTT to
                # increase the window size, rather than doing it on ACK.
                self.set_window_size(time, cwnd + 1. / cwnd)

    def handle_timeout(self, packet, time):
        if self.last_drop is None or \
           time - self.last_drop > TCPTahoe.TIMEOUT_TOLERANCE:
            self.ss = True
            self.ssthresh = max(self.host.cwnd / 2, TCPTahoe.INITIAL_CWND)
            self.set_window_size(time, TCPTahoe.INITIAL_CWND)

            self.last_drop = time

            Logger.warning(time, "Timeout Received. SS_Threshold -> %d" % self.ssthresh)
