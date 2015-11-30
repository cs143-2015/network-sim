from packet import Packet


class AckPacket(Packet):
    ACK_PACKET_SIZE = 64

    def __init__(self, flow_id, src, dest, request_number):
        self.flow_id = flow_id
        self.request_number = request_number

        identifier = "%s.%d" % (self.flow_id, self.request_number)

        super(AckPacket, self).__init__(identifier, src, dest)

    def size(self):
        """
        Size of packet is the size of the header
        """
        return super(AckPacket, self).size() + 2 * 8

    def __repr__(self):
        return "Ack(flow=%s, Rn=%d)" % (self.flow_id, self.request_number)
