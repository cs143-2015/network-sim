from events.event_types.event import Event
from utils import Logger


class WindowSizeEvent(Event):
    def __init__(self, time, flow_id, window_size):
        super(WindowSizeEvent, self).__init__(time)
        self.flow_id = flow_id
        self.window_size = window_size

    def execute(self):
        # This is used for graphing, so no need to do anything here
        pass

    def __repr__(self):
        return "WindowSizeEvent<%s : %.1f>" % (self.flow_id, self.window_size)
