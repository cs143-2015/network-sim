from graph_event import GraphEvent
from utils import Logger


class WindowSizeEvent(GraphEvent):
    def __init__(self, time, flow_id, window_size):
        super(WindowSizeEvent, self).__init__(time)
        self.flow_id = flow_id
        self.window_size = window_size

    def __repr__(self):
        return "WindowSizeEvent<%s : %.1f>" % (self.flow_id, self.window_size)

    def identifier(self):
        return self.flow_id

    def y_value(self):
        return self.window_size
