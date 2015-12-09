from graph_event import GraphEvent


class RTTEvent(GraphEvent):
    def __init__(self, flow_id, time, rtt):
        super(RTTEvent, self).__init__(time)
        self.flow_id = flow_id
        self.rtt = rtt

    def __repr__(self):
        return "RTTEvent<%5.2f : %5.2f>" % (self.time, self.rtt)

    def identifier(self):
        return self.flow_id

    def y_value(self):
        return self.rtt
