from packet import Packet


class RoutingPacket(Packet):
    # Auto-incrementing routing ID index
    ROUTING_INDEX = 0

    def __init__(self, cost_table, src, dest):
        identifier = self.get_packet_id()
        super(RoutingPacket, self).__init__(identifier, src, dest)
        self.costTable = cost_table

    def size(self):
        """
        Size of routing packet is the size of the header plus the size of the
        cost_table dictionary (dictionary of 8-byte ints). Size is in bytes.
        """
        return super(RoutingPacket, self).size() + 2 * 8 * len(self.costTable)

    def __repr__(self):
        return "Routing(src=%s table=%s)" % (self.src, self.costTable)

    @classmethod
    def get_packet_id(cls):
        packet_id = "R.%d" % cls.ROUTING_INDEX
        cls.ROUTING_INDEX += 1
        return packet_id
