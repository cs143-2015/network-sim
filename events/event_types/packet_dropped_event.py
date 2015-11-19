from events.event_types.event import Event
from utils import Logger


class PacketDroppedEvent(Event):
    def __init__(self, time, host, flow, expected_id):
        super(PacketDroppedEvent, self).__init__(time)
        self.host = host
        self.flow = flow
        self.expected_id = expected_id

    def execute(self):
        msg = "Packet dropped; Host %s expected packet %s.%d" % (self.host, self.flow.id, self.expected_id)
        Logger.debug(self.time, msg)

        self.flow.packet_dropped(self.time, self.expected_id)
