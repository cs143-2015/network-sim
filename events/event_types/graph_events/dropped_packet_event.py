from graph_event import GraphEvent


class DroppedPacketEvent(GraphEvent):
    def __init__(self, time, link_id):
        super(DroppedPacketEvent, self).__init__(time)
        self.linkId = link_id

    def __repr__(self):
        return "DroppedPacketEvent<%s>" % self.linkId

    def identifier(self):
        return self.linkId

    def y_value(self):
        return 1
