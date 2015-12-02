from collections import namedtuple
from copy import deepcopy

from components.network import Network
from components.packet_types import AckPacket, Packet, RoutingPacket
from errors import UnhandledPacketType
from events.event_types import PacketSentToLinkEvent
from node import Node
from utils import Logger

LinkCostTuple = namedtuple("LinkCostTuple", ["link", "cost"])


class Router(Node):
    """
    :type links: list[Links]
    :type routingTable: dict[str, LinkCostTuple]
    """
    def __init__(self, identifier):
        """
        A network router.

        Args:
            id (str):   The name of the router.
        """
        super(Router, self).__init__(identifier)
        # List of Links
        self.links = []
        # { node_id : LinkCostTuple }
        self.routingTable = None
        self.dynamicRoutingTable = None

    def __repr__(self):
        return "Router[%s]" % self.id

    def add_link(self, link):
        """
        Adds the given link to the router

        :param link: Link to add
        :type link: Link
        :return: Nothing
        :rtype: None
        """
        if link in self.links:
            return
        self.links.append(link)

    def receive(self, packet, time):
        """
        Handles receipt of a packet.

        Args:
            packet (Packet):                The packet.
        """
        Logger.info(time, "%s received packet %s" % (self, packet))
        # Update the current routing table with the routing packet
        if isinstance(packet, RoutingPacket):
            self.handle_routing_packet(packet)
        # Route the packet
        elif isinstance(packet, AckPacket) or isinstance(packet, Packet):
            if not self.routingTable:
                Logger.warning(time, "%s dropped packet %s, no routing table. "
                                     "Creating one now." % (self, packet))
                self.create_routing_table()
                return
            elif packet.dest.id not in self.routingTable:
                # TODO: should we keep a packet queue for packets w/o dest.?
                Logger.warning(time, "%s dropped packet %s, dest. not in "
                                     "routing table." % (self, packet))
                return
            dest_link = self.routingTable[packet.dest.id].link
            self.send(packet, dest_link, time)
        else:
            raise UnhandledPacketType

    def send(self, packet, link, time):
        """
        Sends the given packet along the link at the specified time

        :param packet: Packet to send
        :type packet: Packet
        :param link: Link to send the packet through
        :type link: Link
        :param time: Time to send the packet
        :type time: float
        :return: Nothing
        :rtype: None
        """
        assert len(self.links) > 0, "Can't send if links aren't connected"
        Logger.info(time, "%s sent packet %s over link %s." % (self, packet, link.id))
        # Send the packet
        self.dispatch(PacketSentToLinkEvent(time, self, packet, link))

    # --------------------- Routing Table Creation -------------------- #
    def create_routing_table(self):
        """
        Begins creation of a routing table by broadcasting adjacent link costs

        :return: Nothing
        :rtype: None
        """
        # Initialize cost of reaching oneself as 0
        self.routingTable = {self.id: LinkCostTuple(None, 0)}
        # Create cost table to broadcast with costs of this router's neighbors
        # { node_id : cost }
        cost_table = {}
        for link in self.links:
            cost = len(link)  # Link cost
            other_node_id = link.other_node(self).id
            cost_table[other_node_id] = cost
            self.routingTable[other_node_id] = LinkCostTuple(link, cost)
        self.broadcast_table(cost_table)

    def broadcast_table(self, cost_table):
        """
        Broadcasts given table to all nodes this router is connected to.

        :param cost_table: Cost table to broadcast
        :type cost_table: dict[str, float]
        :return: Nothing
        :rtype: None
        """
        for link in self.links:
            packet = RoutingPacket(deepcopy(cost_table), self, link.other_node(self))
            self.send(packet, link, Network.get_time())

    def handle_routing_packet(self, packet):
        """
        Updates the cost and routing tables using the given routing packet

        :param packet: Routing packet to update tables for
        :type packet: RoutingPacket
        :return: Nothing
        :rtype: None
        """
        # No routing table yet. Begin creation, then handle this packet
        if not self.routingTable:
            self.create_routing_table()
        did_update = False
        cost_table = packet.costTable
        src_id = packet.src.id

        # Update costs by adding the cost to travel to the source node
        src_cost = self.routingTable[src_id].cost
        for identifier in cost_table.keys():
            cost_table[identifier] = cost_table[identifier] + src_cost

        src_link = self.routingTable[src_id].link
        # Update our routing table based on the received table
        for identifier, cost in cost_table.items():
            # New entry to tables or smaller cost
            if identifier not in self.routingTable or \
                    cost < self.routingTable[identifier].cost:
                did_update = True
                self.routingTable[identifier] = LinkCostTuple(src_link, cost)

        # Broadcast the updated table if an update occurred
        if did_update:
            self.broadcast_table(self.cost_table_from_routing_table())
        else:
            # Log finalized routing table
            Logger.debug(Network.get_time(), "%s final routing table:" % self)
            for i, j in self.routingTable.items():
                Logger.debug(Network.get_time(), "\t%s: %s" % (i, j))

    def link_connected_to_node(self, node_id):
        """
        Returns the link that is connected to the node with the given id

        :param node_id: Node id to get connecting link for
        :type node_id: str
        :return: Connecting link
        :rtype: Link
        """
        for link in self.links:
            if link.other_node(self).id == node_id:
                return link
        raise ValueError("There's no link that connects %s to a "
                         "node with id: %s" % (self, node_id))

    def cost_table_from_routing_table(self):
        """
        Creates a cost table that creates a cost table from the routing table by
        excluding the cost of reaching oneself and links in the routing table.

        :return: Cost table
        :rtype: dict[str, float]
        """
        cost_table = {}
        for node_id, link_cost in self.routingTable.items():
            # Don't include this router in the cost table (cost is always 0)
            if node_id == self.id:
                continue
            cost_table[node_id] = link_cost.cost
        return cost_table
