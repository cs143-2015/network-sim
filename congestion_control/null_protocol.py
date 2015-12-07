from protocol import Protocol


class NullProtocol(Protocol):
    INITIAL_CWND = 1e10

    def __init__(self, host):
        super(NullProtocol, self).__init__(host)

    def handle_send(self, packet, time):
        pass

    def handle_receive(self, packet, time):
        pass

    def handle_timeout(self, packet, time):
        pass
