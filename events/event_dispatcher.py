class EventDispatcher:
    def __init__(self):
        """
        An event queue that process events at a specific time.
        """

        self.queue = []

    def push(self, event):
        """
        Adds an event to the queue

        Args:
            event (Event):  The event to enqueue.
        """
        pass

    def execute(self, time):
        """
        Executes all events that were to be dispatched by the current time.

        Args:
            time (int): The current time.
        """
        pass

    def listen(self, component):
        """
        Listens to a network component for events.

        Args:
            component (EventTarget):    The component that will dispatch events.
        """
        pass
