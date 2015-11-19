from events.event_types.event import Event


class FlowPacketReceivedEvent(Event):
    def __init__(self, time, packet, flow):
        super(FlowPacketReceivedEvent, self).__init__(time)
        self.packet = packet
        self.flow = flow
        self.time = time

    def execute(self):
        self.flow.destination_received(self.packet, self.time)

    def __repr__(self):
        return "FlowPacketReceived<%s <= %s>" % (self.packet.dest, self.packet)
