from events.event_types.event import Event
from utils import Logger


class AckReceivedEvent(Event):
    def __init__(self, time, host, flow):
        super(AckReceivedEvent, self).__init__(time)
        self.host = host
        self.flow = flow

    def execute(self):
        msg = "ACK received from host %s, flow %s" % (self.host, self.flow)
        Logger.debug(self.time, msg)

        self.flow.ack_received(self.time)
