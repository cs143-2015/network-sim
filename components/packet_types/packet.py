class Packet(object):
    def __init__(self, identifier, payload, src, dest):
        """
        A network packet.

        Args:
            identifier (str):   ID for the packet.
            payload (int[]):    Actual byte data payload; may be an ACK.
            src (Host):         Source host.
            dest (Host):        Destination host.
        """
        self.id = identifier
        self.payload = payload
        self.src = src
        self.dest = dest

    def size(self):
        return len(self.payload)

    def __repr__(self):
        return "Packet(id=%s,size=%i)" % (self.id, self.size())
