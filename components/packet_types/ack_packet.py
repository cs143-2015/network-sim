from packet import Packet


class AckPacket(Packet):
    ACK_PACKET_SIZE = 64

    def __init__(self, flow, src, dest, request_number):
        self.flow = flow
        self.request_number = request_number

        identifier = "%s.%d" % (self.flow.id, self.request_number)

        super(AckPacket, self).__init__(None, list(identifier), src, dest)

    def __repr__(self):
        return "Ack(flow=%s, Rn=%d)" % (self.flow.id, self.request_number)
