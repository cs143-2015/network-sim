from events.event_types.event import Event


class PacketSentEvent(Event):
    def __init__(self, time, origin, packet, link):
        super(PacketSentEvent, self).__init__(time)
        self.packet = packet
        self.origin = origin
        self.link = link

    def execute(self):
        self.link.send(self.time, self.packet, self.origin)

    def __repr__(self):
        return "PacketSent<%s over %s from %s>" % (self.packet, self.link, self.origin)
