from packet import Packet


class RoutingPacket(Packet):

    def __init__(self, cost_table, src, dest):
        super(RoutingPacket, self).__init__(None, src, dest)
        self.costTable = cost_table

    def size(self):
        """
        Size of routing packet is the size of the header plus the size of the
        cost_table dictionary (dictionary of 8-byte ints)
        """
        return super(RoutingPacket, self).size() + 2 * 8 * len(self.costTable)

    def __repr__(self):
        return "Routing(src=%s table=%s)" % (self.src, self.costTable)
