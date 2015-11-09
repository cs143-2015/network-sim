from packet import Packet


class AckPacket(Packet):
    ACK_PACKET_SIZE = 64

    def __init__(self, ack_id, src, dest):
        super(AckPacket, self).__init__(None, list(ack_id), src, dest)

    def __repr__(self):
        return "Ack(id=%s)" % "".join(self.payload)
