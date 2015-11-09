from events.event_types.event import Event
from components.packet_types import FlowPacket


class TimeoutEvent(Event):

    # Default timeout period
    TIMEOUT_PERIOD = 100

    def __init__(self, time, host, packet):

        super(TimeoutEvent, self).__init__(time)
        self.host = host
        self.packet = packet

    def execute(self):
        resent = self.host.resend_if_necessary(self.packet.id, self.time)
        if resent and isinstance(self.packet, FlowPacket):
            self.packet.flow.timeout_received(self.time)

    def __repr__(self):
        return "TimeoutEvent<%s : %s>" % (self.host, self.packet.id)
