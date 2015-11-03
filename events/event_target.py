class EventTarget(object):
    def __init__(self):
        """
        An object that dispatches events.
        """

        self.listeners = []

    def dispatch(self, event):
        """
        Dispatches an event to all listeners.

        Args:
            event (Event):  The event to dispatch.
        """
        pass

    def addListener(self, listener):
        """
        Recognizes a listener that is subscribed to this event target's events.

        Args:
            listener (EventDispatcher): The listener.
        """
        pass
