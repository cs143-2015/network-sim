from graph_event import GraphEvent


class LinkBufferSizeEvent(GraphEvent):
    def __init__(self, time, link_id, buffer_size):
        super(LinkBufferSizeEvent, self).__init__(time)
        self.link_id = link_id
        self.buffer_size = buffer_size

    def __repr__(self):
        return "LinkBufferSizeEvent<%s : %d>" % (self.link_id, self.buffer_size)

    def identifier(self):
        return self.link_id

    def y_value(self):
        return self.buffer_size
