from packet import Packet


class FlowPacket(Packet):
    FLOW_PACKET_SIZE = 1024  # 1 KB for flow-generated data packets

    def __init__(self, flow_id, packet_index, size, src, dest):
        self.flow_id = flow_id
        self.sequence_number = packet_index
        self.packet_size = size

        packet_id = "%s.%s" % (flow_id, packet_index)
        super(FlowPacket, self).__init__(packet_id, src, dest)

    def size(self):
        """
        Size of packet is the size of the header and the actual payload size.
        Size is in bytes.
        """
        return FlowPacket.FLOW_PACKET_SIZE

    def __repr__(self):
        return "Flow(id=%s)" % self.id
