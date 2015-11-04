class EventTarget(object):
    def __init__(self):
        """
        An object that dispatches events.
        """
        self.listeners = []

    def dispatch(self, event):
        """
        Dispatches an event to all listeners.

        :param event: The event to dispatch.
        :type event: Event
        :return: Nothing
        :rtype: None
        """
        for listener in self.listeners:
            listener.push(event)

    def add_listener(self, listener):
        """
        Recognizes a listener that is subscribed to this event target's events.

        :param listener: The listener.
        :type listener: EventDispatcher
        :return: Nothing
        :rtype: None
        """
        if listener in self.listeners:
            return
        self.listeners.append(listener)
