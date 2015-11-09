from packet_types import FlowPacket
from events import EventTarget
from events.event_types import WindowSizeEvent
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
        self.amount = amount * 1024 * 1024
        self.start_time = start_time * 1000
        self.window_size = 1
        self.current_packet = 1
        self.total_size = 0

    def start(self):
        self.send_packet()
        self.dispatch(WindowSizeEvent(self.start_time, self.id, self.window_size))

    def send_packet(self, time=None):
        n = 0
        if time == None:
            time = self.start_time
        while self.total_size < self.amount and n < self.window_size:
            size = int(min(self.amount - self.total_size, FlowPacket.FLOW_PACKET_SIZE))
            packet = FlowPacket(self, self.current_packet, size, self.src, self.dest)

            self.src.send(packet, time)

            self.total_size += size
            self.current_packet += 1
            n += 1

    def ack_received(self, time):
        self.window_size += 1 / float(self.window_size)
        Logger.debug(time, "ACK Received. Window size now at %0.1f for flow %s" % (self.window_size, self.id))
        self.dispatch(WindowSizeEvent(time, self.id, self.window_size))
        self.send_packet(time)

    def timeout_received(self, time):
        self.window_size /= 1.1
        if self.window_size < 1:
            self.window_size = 1
        self.dispatch(WindowSizeEvent(time, self.id, self.window_size))
        Logger.debug(time, "Timeout Received. Window size now at %0.1f for flow %s" % (self.window_size, self.id))

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
