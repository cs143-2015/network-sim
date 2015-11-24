from components.packet_types import FlowPacket
from events.event_types import LinkBufferSizeEvent

class LinkBuffer:
    def __init__(self, link):
        self.link = link
        self.buffers = {
            1: [],
            2: []
        }

    def add_to_buffer(self, packet, destination_id, time):
        if destination_id in self.buffers:
            self.buffers[destination_id].append(packet)
        else:
            raise Exception("Packet being added to link buffer but not going through link")
        self.update_buffer_size(time)

    def pop_from_buffer(self, destination_id, time):
        if destination_id not in self.buffers:
            raise Exception("Packet being popped from nonexistent link buffer but not going through link")
        if len(self.buffers[destination_id]) == 0:
            return
        packet = self.buffers[destination_id].pop(0)
        self.update_buffer_size(time)
        return packet

    def update_buffer_size(self, time):
        event = LinkBufferSizeEvent(time, self.link.id, self.size() / FlowPacket.FLOW_PACKET_SIZE)
        self.link.dispatch(event)

    def size(self):
        sum_fn = lambda total, packet: total + packet.size()
        return reduce(sum_fn, self.buffers[1] + self.buffers[2], 0)
