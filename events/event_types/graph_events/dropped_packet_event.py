from graph_event import GraphEvent
from utils import Logger


class DroppedPacketEvent(GraphEvent):
    def __init__(self, time, link_id, amount_dropped):
        super(DroppedPacketEvent, self).__init__(time)
        self.linkId = link_id
        self.amountDropped = amount_dropped

    def __repr__(self):
        return "DroppedPacketEvent<%s : %d>" % (self.linkId, self.amountDropped)

    def identifier(self):
        return self.linkId

    def y_value(self):
        return self.amountDropped
