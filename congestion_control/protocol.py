import abc


class Protocol(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host):
        self.host = host

    @abc.abstractmethod
    def handle_send(self, packet, time):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_receive(self, packet, time):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_timeout(self, packet, time):
        raise NotImplementedError

    def set_window_size(self, time, value):
        self.host.set_window_size(time, value)
