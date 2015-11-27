import abc


class Event(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, time):
        """
        A generic event.

        Args:
            time (int):   The time at which the event occurs.
        """
        self.time = time

    @abc.abstractmethod
    def execute(self):
        """
        Execute the event.
        """
        raise NotImplementedError
