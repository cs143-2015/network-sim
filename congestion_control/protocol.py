class Protocol(object):
    def __init__(self, host):
        self.host = host

    def handle_send(self, packet, time):
        raise Exception("not yet implemented")

    def handle_receive(self, packet, time):
        raise Exception("not yet implemented")

    def handle_timeout(self, packet, time):
        raise Exception("not yet implemented")

    def set_window_size(self, time, value):
        self.host.set_window_size(time, value)
