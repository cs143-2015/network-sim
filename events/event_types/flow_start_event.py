from events.event_types.event import Event


class FlowStartEvent(Event):
    def __init__(self, time, host, flow_id):
        super(FlowStartEvent, self).__init__(time)
        self.time = time
        self.host = host
        self.flow_id = flow_id

    def execute(self):
        self.host.send_packets(self.time, self.flow_id)

    def __repr__(self):
        return "FlowStart<%s : %s>" % (self.host, self.flow_id)
