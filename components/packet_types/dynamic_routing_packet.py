from routing_packet import RoutingPacket


class DynamicRoutingPacket(RoutingPacket):
    """
    Routing packet used for dynamic routing
    """
    # Auto-incrementing routing ID index
    ROUTING_INDEX = 0
    # Identifier Prefix
    ID_PREFIX = "DR."

    def __init__(self, cost_table, src, dest):
        identifier = self._get_packet_id()
        super(DynamicRoutingPacket, self).\
            __init__(identifier, src, dest, cost_table)

    def __repr__(self):
        return "DynamicRouting(src=%s table=%s)" % (self.src, self.costTable)

    @classmethod
    def _get_packet_id(cls):
        """
        Private method, used to get the auto-incrementing routing packet ID

        :return: Packet ID
        :rtype: str
        """
        packet_id = cls.ID_PREFIX + str(cls.ROUTING_INDEX)
        cls.ROUTING_INDEX += 1
        return packet_id
