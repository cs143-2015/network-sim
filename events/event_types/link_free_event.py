from events.event_types.event import Event
from utils import Logger


class LinkFreeEvent(Event):
    def __init__(self, time, link, direction, packet):
        super(LinkFreeEvent, self).__init__(time)
        self.link = link
        self.direction = direction
        self.packet = packet

    def execute(self):
        # If the packet that was sent to trigger this link free event is still
        # on the link, that's fine; this event is what means that it's off the
        # link, so we can remove it.
        if self.packet in self.link.packets_on_link[3 - self.direction]:
            self.link.packets_on_link[3 - self.direction].remove(self.packet)
        # Now, we check that there's nothing on the other side of the link.
        # If the link is currently sending data in the other direction, we
        # can't do anything here.
        if self.link.packets_on_link[3 - self.direction] != []:
            return

        destination = self.link.get_node_by_direction(self.direction)
        origin = self.link.get_node_by_direction(3 - self.direction)

        Logger.debug(self.time, "Link %s freed towards node %d (%s)" %
                     (self.link.id, self.direction, destination))
        self.link.in_use = False
        self.link.current_dir = None

        next_packet_in_dir = self.link.buffer.pop_from_buffer(self.direction, self.time)
        if next_packet_in_dir is not None:
            Logger.debug(self.time, "Buffer exists toward node %d" % (self.direction))
            self.link.send(self.time, next_packet_in_dir, origin, from_free=True)

    def __repr__(self):
        return "LinkFree<link=%s,dir=%d>" % (self.link, self.direction)
