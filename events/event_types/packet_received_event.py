from events.event_types.event import Event
from utils import Logger


class PacketReceivedEvent(Event):
    def __init__(self, time, packet, destination, link):
        super(PacketReceivedEvent, self).__init__(time)
        self.packet = packet
        self.destination = destination
        self.link = link

    def execute(self):
        Logger.info(self.time, "Packet %s received at %s" % (self.packet, self.destination))
        self.link.packets_on_link[self.link.get_direction_by_node(self.destination)].remove(self.packet)
        self.destination.receive(self.packet, self.time)

    def __repr__(self):
        return "PacketReceived<%s <= %s>" % (self.destination, self.packet)
