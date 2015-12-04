from collections import deque

from components.packet_types import FlowPacket
from events.event_types.graph_events import LinkBufferSizeEvent
from utils.logger import Logger


class LinkBuffer:
    """
    :type link: Link
    :type buffers: dict[int, deque[Packet]]
    :type entry_times: dict[str, int]
    :type avg_buffer_time: int
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
        # Dictionary containing entry times for packets into the buffer.
        self.entry_times = {}
        # Average amount of time a packet spends in the buffer
        self.avg_buffer_time = 0

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
            self.buffers[destination_id].append(packet)
        else:
            raise Exception("Packet being added to link buffer but not going "
                            "through link")
        self.update_buffer_size(time)
        # Track packet entry time into buffer
        self.entry_times[packet.id] = time

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
        packet = self.buffers[destination_id].popleft()
        self.update_buffer_size(time)
        self.handle_packet_exit_from_buffer(packet.id, time)
        return packet

    def handle_packet_exit_from_buffer(self, identifier, exit_time):
        """
        Pops the identifier from the entry times and updates the avg buffer time

        :param identifier: Identifier to add to the buffer times
        :type identifier: str
        :param exit_time: Time the packet exited the buffer
        :type exit_time: int
        """
        entry_time = self.entry_times.pop(identifier, None)
        if entry_time is None:
            msg = "Packet with id: %s never entered buffer. But was popped " \
                  "from the buffer." % identifier
            Logger.warning(exit_time, msg)
            return
        buffer_time = exit_time - entry_time
        assert buffer_time >= 0, \
            "A packet can't spend a negative amount of time in the buffer"
        self.avg_buffer_time = (self.avg_buffer_time + buffer_time) / 2.0
        Logger.debug(exit_time, "%s: Average buffer delay is now %f"
                                % (self, self.avg_buffer_time))

    def reset_buffer_time(self, time):
        """
        Resets the average buffer time

        :param time: Time when this reset is taking place
        :type time: float
        """
        Logger.debug(time, "%s: Resetting buffer time." % self)
        self.avg_buffer_time = 0

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
        Get the size of the buffer.

        :return: Size of the buffer
        :rtype: int
        """
        sum_fn = lambda total, packet: total + packet.size()
        items = list(self.buffers[self.NODE_1_ID]) + list(self.buffers[self.NODE_2_ID])
        return reduce(sum_fn, items, 0)
