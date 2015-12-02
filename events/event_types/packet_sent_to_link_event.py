from events.event_types.event import Event
from utils import Logger


class PacketSentToLinkEvent(Event):
    def __init__(self, time, origin, packet, link):
        super(PacketSentToLinkEvent, self).__init__(time)
        self.packet = packet
        self.origin = origin
        self.link = link

    def execute(self):
        Logger.info(self.time, "Packet %s sent to link %s from %s" % (self.packet, self.link.id, self.origin))
        self.link.send(self.time, self.packet, self.origin)

    def __repr__(self):
        return "PacketSentToLink<%s over %s from %s>" % (self.packet, self.link, self.origin)
