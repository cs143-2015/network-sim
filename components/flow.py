from packet_types.packet import Packet
from events import EventTarget

class Flow(EventTarget):
    def __init__(self, id, src, dest, amount, start_time):
        """
        A network flow.

        Args:
            id (str):       The name of the flow.
            src (Host):     The source host.
            dest (Host):    The destination host.
            amount (int):   The amount of data to send, in MB.
            start_time (float):  The time at which the flow starts, in s.
        """
        super(EventTarget, self).__init__()
        self.id = id
        self.src = src
        self.dest = dest
        self.amount = amount * 1024 * 1024
        self.start_time = start_time

    def start(self):
        total_size = 0
        n = 1
        while total_size < self.amount:
            # TODO: Use FlowPacket subclass instead
            size = int(min(self.amount - total_size, Packet.FLOW_PACKET_SIZE))
            payload = [1 for i in range(size)]
            if size < Packet.FLOW_PACKET_SIZE:
                payload += [0 for i in range(Packet.FLOW_PACKET_SIZE - size)]
            assert len(payload) == Packet.FLOW_PACKET_SIZE

            packet_id = "%s.%s" % (self.id, n)
            packet = Packet(packet_id, payload, self.src, self.dest)

            self.src.send(packet, self.start_time * 1000)

            total_size += Packet.FLOW_PACKET_SIZE
            n += 1
