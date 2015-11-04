import abc


class Event(object):
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
