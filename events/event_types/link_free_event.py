from events.event_types.event import Event
from utils import Logger


class LinkFreeEvent(Event):
    def __init__(self, time, link, direction):
        self.time = time
        self.link = link
        self.direction = direction

    def execute(self):
        if self.link.current_dir is not None and self.link.current_dir != self.direction:
            # If the link is currently sending data in the other direction, we
            # can't do anything here.
            return

        destination = self.link.get_node_by_direction(self.direction)
        origin = self.link.get_node_by_direction(3 - self.direction)

        Logger.debug(self.time, "Link %s freed towards node %d (%s)" % (self.link.id, self.direction, destination))
        self.link.in_use = False
        self.link.current_dir = None

        next_packet_in_dir = self.link.buffer.pop_from_buffer(self.direction, self.time)
        if next_packet_in_dir is not None:
            Logger.debug(self.time, "Buffer exists toward node %d" % (self.direction))
            self.link.send(self.time, next_packet_in_dir, origin)

    def __repr__(self):
        return "LinkFree<link=%s,dir=%d>" % (self.link, self.direction)
