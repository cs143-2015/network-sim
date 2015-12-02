from events.event_types.event import Event
from packet_received_event import PacketReceivedEvent
from utils import Logger


class PacketSentOverLinkEvent(Event):
    def __init__(self, time, packet, destination, link):
        super(PacketSentOverLinkEvent, self).__init__(time)
        self.packet = packet
        self.destination = destination
        self.link = link

    def execute(self):
        Logger.info(self.time, "Packet %s sent over link %s to %s" % (self.packet, self.link.id, self.destination))
        transmission_delay = self.link.transmission_delay(self.packet)
        recv_time = self.time + transmission_delay + self.link.delay
        self.link.dispatch(PacketReceivedEvent(recv_time, self.packet, self.destination))

    def __repr__(self):
        return "PacketSentOverLink<%s over %s to %s>" % (self.packet, self.link, self.destination)
