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

    def add_timer(self, event, time, interval):
        """
        Add the timer for the event to the listener

        :param event: Event to execute periodically
        :type event: Event
        :param time: Time when the timer was added
        :type time: float
        :param interval: Interval to execute the event in
        :type interval: float
        :return: Nothing
        :rtype: None
        """
        for listener in self.listeners:
            listener.add_timer(event, time, interval)
