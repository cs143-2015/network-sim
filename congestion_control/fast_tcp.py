from protocol import Protocol
from components.packet_types import AckPacket


class FAST_TCP(Protocol):
    INITIAL_CWND = 1
    ALPHA = 15
    UPDATE_INTERVAL = 200

    def __init__(self, host):
        super(FAST_TCP, self).__init__(host)

        self.sent_packets = {}
        self.rtts = []
        self.rtt_min = None

        self.last_update = None

    def handle_send(self, packet, time):
        self.sent_packets[packet] = time

    def handle_receive(self, packet, time):
        if isinstance(packet, AckPacket):
            if packet.trigger_packet in self.sent_packets:
                rtt = time - self.sent_packets[packet.trigger_packet]
                self.rtts.append(rtt)
                if self.rtt_min is None or rtt < self.rtt_min:
                    self.rtt_min = rtt
            self.update_window_size(time)

    def handle_timeout(self, packet, time):
        pass

    def update_window_size(self, time):
        if self.last_update is None or \
           time - self.last_update > FAST_TCP.UPDATE_INTERVAL:
            cwnd = self.rtt_min / float(self.rtts[-1]) * self.host.cwnd + FAST_TCP.ALPHA
            self.set_window_size(time, cwnd)
            self.last_update = time
