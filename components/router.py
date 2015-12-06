from collections import namedtuple
from copy import deepcopy

from components.network import Network
from components.packet_types import AckPacket, Packet, StaticRoutingPacket, \
    DynamicRoutingPacket
from errors import UnhandledPacketType
from events.event_types import PacketSentToLinkEvent, \
    UpdateDynamicRoutingTableEvent
from node import Node
from utils import Logger

LinkCostTuple = namedtuple("LinkCostTuple", ["link", "cost"])


class Router(Node):
    """
    :type links: list[Links]
    :type routingTable: dict[str, LinkCostTuple]
    :type dynamicRoutingTable: dict[str, LinkCostTuple]
    """
    # Interval after which we should begin creating a new dynamic routing table
    DYNAMIC_UPDATE_INTERVAL = 5000
    # Times the same data should be observed before we stop broadcasting updates
    SAME_DATA_THRESHOLD = 2

    def __init__(self, identifier, dynamic_enabled):
        """
        A network router.

        Args:
            identifier (str):       The name of the router.
            dynamic_enabled (bool): Whether we should use dynamic/static routing
        """
        super(Router, self).__init__(identifier)
        self.dynamicEnabled = dynamic_enabled
        # List of Links
        self.links = []
        # { node_id : LinkCostTuple }
        self.routingTable = None
        self.dynamicRoutingTable = None
        self.newDynamicRoutingTable = None
        # Number of times the same data has been received
        self.sameDataCounter = 0
        # Whether the dynamic routing table timer has been added
        self.dynamicRoutingTableTimerAdded = False

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
            time (float):                   Time the packet was received
        """
        Logger.info(time, "%s received packet %s" % (self, packet))
        # Get the appropriate routing table
        routing_table = self.get_routing_table()
        # Update the current routing table with the routing packet
        if isinstance(packet, StaticRoutingPacket):
            self.handle_routing_packet(packet, dynamic=False)
        elif isinstance(packet, DynamicRoutingPacket):
            self.handle_routing_packet(packet, dynamic=True)
        # Route the packet
        elif isinstance(packet, AckPacket) or isinstance(packet, Packet):
            if not routing_table:
                Logger.warning(time, "%s dropped packet %s, no routing table. "
                                     "Creating one now." % (self, packet))
                self.create_routing_table(self.dynamicEnabled)
                return
            elif packet.dest.id not in routing_table:
                # TODO: should we keep a packet queue for packets w/o dest.?
                Logger.warning(time, "%s dropped packet %s, dest. not in "
                                     "routing table." % (self, packet))
                return
            dest_link = routing_table[packet.dest.id].link
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
        # Send the packet
        self.dispatch(PacketSentToLinkEvent(time, self, packet, link))

    # --------------------- Routing Table Creation -------------------- #
    def create_routing_table(self, dynamic=None):
        """
        Begins creation of a routing table by broadcasting adjacent link costs

        :param dynamic: Whether to create a dynamic or static routing table
        :type dynamic: bool
        :return: Nothing
        :rtype: None
        """
        if not dynamic:
            dynamic = self.dynamicEnabled
        # Only add the dynamic routing table update timer once
        if dynamic and not self.dynamicRoutingTableTimerAdded:
            self.add_timer(UpdateDynamicRoutingTableEvent(None, self),
                           Network.get_time(), self.DYNAMIC_UPDATE_INTERVAL)
            self.dynamicRoutingTableTimerAdded = True
        # Reset the dynamic routing table same data counter
        self.sameDataCounter = 0
        # Initialize cost of reaching oneself as 0
        routing_table = {self.id: LinkCostTuple(None, 0)}
        # Create cost table to broadcast with costs of this router's neighbors
        # { node_id : cost }
        cost_table = {}
        for link in self.links:
            # Get the dynamic or static cost of the link
            cost = link.dynamic_cost() if dynamic else link.static_cost()
            other_node_id = link.other_node(self).id
            cost_table[other_node_id] = cost
            routing_table[other_node_id] = LinkCostTuple(link, cost)
        self.store_routing_table(dynamic, routing_table)
        self.broadcast_table(cost_table, dynamic)

    def broadcast_table(self, cost_table, dynamic):
        """
        Broadcasts given table to all nodes this router is connected to.

        :param cost_table: Cost table to broadcast
        :type cost_table: dict[str, float]
        :param dynamic: Whether we're broadcasting dynamic/static routing table
        :type dynamic: bool
        :return: Nothing
        :rtype: None
        """
        packet_type = DynamicRoutingPacket if dynamic else StaticRoutingPacket
        for link in self.links:
            packet = packet_type(deepcopy(cost_table), self, link.other_node(self))
            self.send(packet, link, Network.get_time())

    def handle_routing_packet(self, packet, dynamic):
        """
        Updates the cost and routing tables using the given routing packet

        :param packet: Routing packet to update tables for
        :type packet: RoutingPacket
        :param dynamic: Whether we're handling a dynamic or static packet
        :type dynamic: bool
        :return: Nothing
        :rtype: None
        """
        # No routing table yet. Begin creation, then handle this packet
        if not self._get_intermediate_routing_table(dynamic):
            self.create_routing_table(dynamic)
        did_update = False
        cost_table = packet.costTable
        src_id = packet.src.id

        # Get the appropriate routing table
        routing_table = self._get_intermediate_routing_table(dynamic)
        # Update costs by adding the cost to travel to the source node
        src_cost = routing_table[src_id].cost
        for identifier in cost_table.keys():
            cost_table[identifier] = cost_table[identifier] + src_cost

        src_link = routing_table[src_id].link
        # Update our routing table based on the received table
        for identifier, cost in cost_table.items():
            # New entry to tables or smaller cost
            if identifier not in routing_table or \
                    cost < routing_table[identifier].cost:
                did_update = True
                routing_table[identifier] = LinkCostTuple(src_link, cost)

        # Store and broadcast the updated table if an update occurred
        if did_update:
            self.sameDataCounter = 0
            self.store_routing_table(dynamic, routing_table)
            new_cost_table = self.cost_table_from_routing_table(dynamic)
            self.broadcast_table(new_cost_table, dynamic)
        else:
            self.sameDataCounter += 1
            # Log the same data receipt
            Logger.debug(Network.get_time(), "%s received no new routing table "
                                             "data." % self)
            # Log finalized routing table
            Logger.trace(Network.get_time(), "%s final %s routing table:"
                         % (self, "dynamic" if dynamic else "static"))
            self.print_routing_table(routing_table)
            if dynamic:
                self.handle_same_dynamic_routing_table()

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

    def cost_table_from_routing_table(self, dynamic):
        """
        Creates a cost table that creates a cost table from the routing table by
        excluding the cost of reaching oneself and links in the routing table.

        :param dynamic: Dynamic routing table if True, else static routing table
        :type dynamic: bool
        :return: Cost table
        :rtype: dict[str, float]
        """
        routing_table = self._get_intermediate_routing_table(dynamic)
        cost_table = {}
        for node_id, link_cost in routing_table.items():
            # Don't include this router in the cost table (cost is always 0)
            if node_id == self.id:
                continue
            cost_table[node_id] = link_cost.cost
        return cost_table

    # --------- Dynamic/Static Routing Table Helpers --------- #
    def get_routing_table(self):
        """
        Get the appropriate routing table to use when routing a packet

        :return: Appropriate routing table
        :rtype: dict[str, LinkCostTuple]
        """
        if not self.dynamicEnabled:
            return self.routingTable
        elif self.dynamicRoutingTable:
            return self.dynamicRoutingTable
        else:
            return self.newDynamicRoutingTable

    def _get_intermediate_routing_table(self, dynamic):
        """
        Get the appropriate intermediate routing table (one used when updating).
        This should only be used when creating the routing table.

        :param dynamic: Dynamic routing table if True, else static routing table
        :type dynamic: bool
        :return: Appropriate routing table
        :rtype: dict[str, LinkCostTuple]
        """
        return self.newDynamicRoutingTable if dynamic else self.routingTable

    def store_routing_table(self, dynamic, routing_table):
        """
        Store the routing table appropriately

        :param dynamic: Dynamic routing table if True, else static routing table
        :type dynamic: bool
        :param routing_table: Routing table to store
        :type routing_table: dict[str, LinkCostTuple]
        :return: Nothing
        :rtype: None
        """
        if dynamic:
            self.newDynamicRoutingTable = routing_table
        else:
            self.routingTable = routing_table

    # ------------- Dynamic Routing Table Helpers ------------ #
    def update_dynamic_routing_table(self, routing_table):
        """
        Replace the old dynamicRoutingTable with the given new one

        :param routing_table: Routing table to update the old one with
        :type routing_table: dict[str, LinkCostTuple]
        :return: Nothing
        :rtype: None
        """
        Logger.trace(Network.get_time(), "Replacing old dynamic routing table:")
        self.print_routing_table(self.dynamicRoutingTable)
        Logger.trace(Network.get_time(), "With new dynamic routing table:")
        self.print_routing_table(self.newDynamicRoutingTable)
        self.dynamicRoutingTable = routing_table

    def handle_same_dynamic_routing_table(self):
        """
        Handle the receipt of a routing table that provided no updates. If we
        have seen the same data SAME_DATA_THRESHOLD times, dispatch an event
        to update the dynamic routing table in the future, and replace the old
        dynamic routing table with the new one. Otherwise re-broadcast the
        routing table.
        """
        if self.sameDataCounter >= self.SAME_DATA_THRESHOLD:
            self.update_dynamic_routing_table(self.newDynamicRoutingTable)
            # Reset the dynamic cost for the links, we're done updating
            map(lambda l: l.reset_dynamic_cost(Network.get_time()), self.links)
            self.sameDataCounter = 0
        else:
            new_cost_table = self.cost_table_from_routing_table(dynamic=True)
            self.broadcast_table(new_cost_table, dynamic=True)

    @staticmethod
    def print_routing_table(routing_table):
        if not routing_table:
            Logger.trace(Network.get_time(), "None")
            return
        for i, j in routing_table.items():
            Logger.trace(Network.get_time(), "\t%s: %s" % (i, j))
