from collections import deque

from components.packet_types import FlowPacket
from events.event_types.graph_events import LinkBufferSizeEvent
from utils.logger import Logger


class LinkBuffer:
    """
    :type link: Link
    :type buffers: dict[int, deque[Packet]]
    :type entryTimes: dict[str, int]
    """
    # ID for specifying the direction of the packet. i.e. to node 1 or to node 2
    NODE_1_ID = 1
    NODE_2_ID = 2

    def __init__(self, link):
        self.link = link
        self.buffers = {
            self.NODE_1_ID: deque(),
            self.NODE_2_ID: deque()
        }
        # Fixed average time a packet spends in the buffer
        self.fixedAvgBufferTime = 0
        # Dynamically updated avgBufferTime
        self.avgBufferTime = 0
        # Entry times of packets into the buffer (used for avgBufferTime calc.)
        self.entryTimes = {}

    def __repr__(self):
        return "LinkBuffer[%s]" % self.link

    def add_to_buffer(self, packet, destination_id, time):
        """
        Adds the given packet to the buffer for the given destination ID

        :param packet: Packet to add
        :type packet: Packet
        :param destination_id: Destination where packet is going (Node 1 or 2)
        :type destination_id: int
        :param time: Time when the packet was added to the buffer
        :type time: int
        """
        if destination_id in self.buffers:
            self.buffers[destination_id].append((packet, time))
        else:
            raise Exception("Packet being added to link buffer but not going "
                            "through link")
        self.update_buffer_size(time)
        # Track packet entry into buffer
        self.entryTimes[packet.id] = time

    def pop_from_buffer(self, destination_id, time):
        """
        Pops a packet from the buffer with the given destination ID

        :param destination_id: Destination ID to get the packet from
        :type destination_id: int
        :param time: Time when the packet was popped
        :type time: int
        :return: Packet from the buffer
        :rtype: Packet
        """
        if destination_id not in self.buffers:
            raise Exception("Packet being popped from nonexistent link buffer "
                            "but not going through link")
        if len(self.buffers[destination_id]) == 0:
            return
        packet = self.buffers[destination_id].popleft()[0]
        self.update_buffer_size(time)
        entry_time = self.entryTimes.pop(packet.id, None)
        if entry_time:
            self.avgBufferTime = (self.avgBufferTime + (time - entry_time)) / 2
        return packet

    def fix_avg_buffer_time(self, time):
        """
        Fixes the average buffer time at the given time. Should be fixed right
        before updating the dynamic routing table.

        :param time: Time to fix the average buffer time at
        :type time: float
        :return: Nothing, access the average buffer time by self.avgBufferTime
        :rtype: None
        """
        self.fixedAvgBufferTime = self.avgBufferTime

    def reset_buffer_metrics(self, time):
        """
        Resets the metrics used by the buffer to calculate average buffer time.
        Should be reset after updating the dynamic routing table.

        :param time: Time when the reset is happening
        :type time: float
        :return: Nothing
        :rtype: None
        """
        Logger.debug(time, "%s: Resetting buffer time." % self)
        self.entryTimes = {}
        self.avgBufferTime = 0

    def get_oldest_packet_and_time(self, destination_id):
        return self.buffers[destination_id][0]

    def update_buffer_size(self, time):
        """
        Dispatch event to track buffer size changes

        :param time: Time to execute the event
        :type time: int
        """
        event = LinkBufferSizeEvent(time, self.link.id,
                                    self.size() / FlowPacket.FLOW_PACKET_SIZE)
        self.link.dispatch(event)

    def size(self):
        """
        Get the size of the buffer in bytes.

        :return: Size of the buffer
        :rtype: int
        """
        sum_fn = lambda total, packet_tuple: total + packet_tuple[0].size()
        items = list(self.buffers[self.NODE_1_ID]) + list(self.buffers[self.NODE_2_ID])
        return reduce(sum_fn, items, 0)
