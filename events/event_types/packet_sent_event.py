from events.event_types.event import Event


class PacketSentEvent(Event):
    def __init__(self, time, packet, link, destination):
        super(PacketSentEvent, self).__init__(time)
        self.packet = packet
        self.link = link
        self.destination = destination

    def execute(self):
        self.link.send(self.packet, self.destination, self.time)

    def __repr__(self):
        return "PacketSent<%s => %s>" % (self.packet, self.destination)
