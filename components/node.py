import abc

from events import EventTarget


class Node(EventTarget):
    """
    Interface for a node in the network graph.
    """
    def __init__(self, identifier):
        super(Node, self).__init__()
        self.id = identifier

    @abc.abstractmethod
    def add_link(self, link):
        """
        Adds the given link to the node

        :param link: Link to add
        :type link: Link
        :return: Nothing
        :rtype: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def receive(self, packet, time):
        """
        Receive the packet at this node

        :param packet: Packet received
        :type packet: Packet
        :param time: Time received
        :type time: int
        :return: Nothing
        :rtype: None
        """
        raise NotImplementedError
