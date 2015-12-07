from utils import Logger
from protocol import Protocol
from components.packet_types import AckPacket, Packet, RoutingPacket, FlowPacket

class TCPReno(Protocol):
    INITIAL_CWND = 2
    INITIAL_SSTHRESH = 1e10
    TIMEOUT_TOLERANCE = 1000
    MAX_DUPLICATES = 4

    def __init__(self, host):
        super(TCPReno, self).__init__(host)

        # Whether the flow is in slow start or not.
        self.ss = True
        # Self Start threshold
        self.ssthresh = TCPReno.INITIAL_SSTHRESH
        # Last drop
        self.last_drop = None
        # Last N request nums
        self.last_n_req_nums = []

    def handle_send(self, packet, time):
        pass

    def handle_receive(self, packet, time):
        if isinstance(packet, AckPacket):
            Rn = packet.request_number

            self.last_n_req_nums.append(Rn)
            if len(self.last_n_req_nums) > TCPReno.MAX_DUPLICATES:
                self.last_n_req_nums.pop(0)

            Sn, Sb, Sm = self.host.sequence_nums
            cwnd = self.host.cwnd
            if self.last_drop is None or \
               time - self.last_drop > TCPReno.TIMEOUT_TOLERANCE:
                print self.last_n_req_nums
                if len(self.last_n_req_nums) == TCPReno.MAX_DUPLICATES and \
                   all(num == Rn for num in self.last_n_req_nums):
                    # If we've had duplicate ACKs, then enter fast retransmit.
                    self.ssthresh = max(self.host.cwnd / 2, TCPReno.INITIAL_CWND)
                    self.set_window_size(time, self.ssthresh)
                    Logger.warning(time, "Duplicate ACKs received for flow %s." % self.host.flow[0])

                    self.last_drop = time
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
           time - self.last_drop > TCPReno.TIMEOUT_TOLERANCE:
            self.ss = True
            self.ssthresh = max(self.host.cwnd / 2, TCPReno.INITIAL_CWND)
            self.set_window_size(time, TCPReno.INITIAL_CWND)

            self.last_drop = time

            Logger.warning(time, "Timeout Received. SS_Threshold -> %d" % self.ssthresh)
