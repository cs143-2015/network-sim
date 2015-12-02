import abc


class Packet(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, identifier, src, dest):
        """
        A network packet.

        Args:
            identifier (str):   ID for the packet.
            src (Host):         Source host.
            dest (Host):        Destination host.
        """
        self.id = identifier
        self.src = src
        self.dest = dest

    def size(self):
        """
        Size of packet is the size of 2, 64-bit integers and str identifier
        (1 byte per char for ASCII string). Size is in bytes.
        """
        return 2 * 8 + len(self.id)

    def __repr__(self):
        return "Packet(id=%s,size=%i)" % (self.id, self.size())
