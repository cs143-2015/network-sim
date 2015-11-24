from events.event_types.event import Event
from utils import Logger


class LinkBufferSizeEvent(Event):
    def __init__(self, time, link_id, buffer_size):
        super(LinkBufferSizeEvent, self).__init__(time)
        self.link_id = link_id
        self.buffer_size = buffer_size

    def execute(self):
        # This is used for graphing, so no need to do anything here
        pass

    def __repr__(self):
        return "LinkBufferSizeEvent<%s : %d>" % (self.link_id, self.buffer_size)
