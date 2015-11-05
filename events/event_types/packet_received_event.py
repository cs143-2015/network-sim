from events.event_types.event import Event


class PacketReceivedEvent(Event):
    def __init__(self, packet, destination, time):
        self.packet = packet
        self.destination = destination
        self.time = time

    def execute(self):
        self.destination.receive(self.packet, self.time)

    def __repr__(self):
        return "PacketReceived<%s <= %s>" % (self.destination, self.packet)
