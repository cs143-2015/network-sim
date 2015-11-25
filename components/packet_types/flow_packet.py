from packet import Packet


class FlowPacket(Packet):
    FLOW_PACKET_SIZE = 1024  # 1 KB for flow-generated data packets

    def __init__(self, flow, packet_index, size, src, dest):
        self.flow = flow
        self.sequence_number = packet_index
        self.packet_size = size

        packet_id = "%s.%s" % (flow.id, packet_index)
        super(FlowPacket, self).__init__(packet_id, [], src, dest)

    def size(self):
        return self.packet_size

    def __repr__(self):
        return "Flow(id=%s)" % self.id
