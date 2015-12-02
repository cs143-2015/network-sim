from events.event_types.event import Event
from components.packet_types import FlowPacket


class TimeoutEvent(Event):

    # Default timeout period
    TIMEOUT_PERIOD = 750

    def __init__(self, time, host, packet):
        super(TimeoutEvent, self).__init__(time)
        self.host = host
        self.packet = packet

    def execute(self):
        self.host.timeout(self.time, self.packet)

    def __repr__(self):
        return "TimeoutEvent<%s : %s>" % (self.host, self.packet.id)
