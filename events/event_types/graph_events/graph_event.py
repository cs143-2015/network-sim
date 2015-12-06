import abc

from events.event_types.event import Event


class GraphEvent(Event):
    __metaclass__ = abc.ABCMeta

    def execute(self):
        # This is used for graphing, so no need to do anything here
        pass

    def x_value(self):
        return self.time

    @abc.abstractmethod
    def identifier(self):
        raise NotImplementedError("Subclass must provide identifier")

    @abc.abstractmethod
    def y_value(self):
        raise NotImplementedError("Subclass must provide y-value")
