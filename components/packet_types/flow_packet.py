from packet import Packet


class FlowPacket(Packet):
    FLOW_PACKET_SIZE = 1024

    def __init__(self, flow, packet_index, size, src, dest):
        self.flow = flow

        payload = [1 for i in range(size)]
        if size < FlowPacket.FLOW_PACKET_SIZE:
            payload += [0 for i in range(FlowPacket.FLOW_PACKET_SIZE - size)]
        assert len(payload) == FlowPacket.FLOW_PACKET_SIZE

        packet_id = "%s.%s" % (flow.id, packet_index)
        super(FlowPacket, self).__init__(packet_id, payload, src, dest)

    def __repr__(self):
        return "Flow(id=%s)" % self.id
