class Packet:
    FLOW_PACKET_SIZE = 1024  # 1 KB for flow-generated data packets
    ACK_PACKET_SIZE = 64

    def __init__(self, payload, src, dest):
        """
        A network packet.

        Args:
            payload (int[]):    Actual byte data payload; may be an ACK.
            src (Host):         Source host.
            dest (Host):        Destination host.
        """
        self.payload = payload
        self.src = src
        self.dest = dest

    def size(self):
        return len(self.payload)

    def __repr__(self):
        return "Packet(%i)" % self.size()
