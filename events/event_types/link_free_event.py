from events.event_types.event import Event
from utils import Logger


class LinkFreeEvent(Event):
    def __init__(self, time, link, direction):
        super(LinkFreeEvent, self).__init__(time)
        self.link = link
        self.direction = direction

    def execute(self):
        if self.link.packets_on_link[3 - self.direction] != []:
            # If the link is currently sending data in the other direction, we
            # can't do anything here.
            return

        destination = self.link.get_node_by_direction(self.direction)
        origin = self.link.get_node_by_direction(3 - self.direction)

        Logger.debug(self.time, "Link %s freed towards node %d (%s)" %
                     (self.link.id, self.direction, destination))
        self.link.in_use = False
        self.link.current_dir = None

        # to1, to2 = map(lambda (k, v): len(v), self.link.buffer.buffers.items())
        # if to1 > 0 and to2 > 0:
        #     print self.link.buffer.get_oldest_packet_and_time(self.direction)
        #     print self.link.buffer.get_oldest_packet_and_time(3 - self.direction)
        #

        next_packet_in_dir = self.link.buffer.pop_from_buffer(self.direction, self.time)
        if next_packet_in_dir is not None:
            Logger.debug(self.time, "Buffer exists toward node %d" % (self.direction))
            self.link.send(self.time, next_packet_in_dir, origin, from_free=True)

    def __repr__(self):
        return "LinkFree<link=%s,dir=%d>" % (self.link, self.direction)
