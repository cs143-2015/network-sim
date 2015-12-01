from events.event_types.event import Event
from utils import Logger


class PacketReceivedEvent(Event):
    def __init__(self, time, packet, destination):
        super(PacketReceivedEvent, self).__init__(time)
        self.packet = packet
        self.destination = destination
        self.time = time

    def execute(self):
        Logger.info(self.time, "Packet %s received at %s" % (self.packet, self.destination))
        self.destination.receive(self.packet, self.time)

    def __repr__(self):
        return "PacketReceived<%s <= %s>" % (self.destination, self.packet)
