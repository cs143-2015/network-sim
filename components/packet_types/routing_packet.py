from packet import Packet


class RoutingPacket(Packet):

    def __init__(self, cost_table, src, dest):
        super(RoutingPacket, self).__init__(None, cost_table, src, dest)

    def __repr__(self):
        return "Routing(src=%s table=%s)" % (self.src, self.payload)
