from events.event_types.event import Event


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

        print "Link freed towards node %d (t = %f)" % (self.direction, self.time)
        self.link.in_use = False
        self.link.current_dir = None

        next_packet_in_dir = self.link.buffer.pop_from_buffer(self.direction)
        if next_packet_in_dir is not None:
            print "Buffer exists toward node %d (t = %f)" % (self.direction, self.time)
            destination = self.link.get_node_by_direction(self.direction)
            self.link.send(next_packet_in_dir, destination, self.time)

    def __repr__(self):
        return "LinkFree<link=%s,dir=%d>" % (self.link, self.direction)
