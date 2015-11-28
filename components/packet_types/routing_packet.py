from packet import Packet


class RoutingPacket(Packet):
    # Auto-incrementing routing ID index
    ROUTING_INDEX = 0

    def __init__(self, cost_table, src, dest):
        identifier = self.get_packet_id()
        super(RoutingPacket, self).__init__(identifier, cost_table, src, dest)

    def __repr__(self):
        return "Routing(src=%s table=%s)" % (self.src, self.payload)

    @classmethod
    def get_packet_id(cls):
        packet_id = "R.%d" % cls.ROUTING_INDEX
        cls.ROUTING_INDEX += 1
        return packet_id
