from graph_event import GraphEvent


class LinkBufferSizeEvent(GraphEvent):
    def __init__(self, time, link_id, buffer_size):
        super(LinkBufferSizeEvent, self).__init__(time)
        self.linkId = link_id
        self.bufferSize = buffer_size

    def __repr__(self):
        return "LinkBufferSizeEvent<%s : %d>" % (self.linkId, self.bufferSize)

    def identifier(self):
        return self.linkId

    def y_value(self):
        return self.bufferSize
