from events.event_types.event import Event
from events.event_types import WindowSizeEvent, LinkBufferSizeEvent
from utils import Logger

class EventDispatcher:
    def __init__(self):
        """
        An event queue that process events at a specific time.
        """
        # Queue containing events to dispatch, keys are dispatch times
        self.queue = {}
        self.graph_events = []

    def push(self, event):
        """
        Adds an event to the queue

        :param event: Event to enqueue
        :type event: Event
        :return: Nothing
        :rtype: None
        """
        time = event.time
        if time in self.queue:
            self.queue[time].append(event)
        else:
            # Set to prevent duplicates??
            self.queue[time] = [event]

    def execute(self, time):
        """
        Executes all events that were to be dispatched by the current time.

        :param time: The current time.
        :type time: int
        :return: True if there are still events left in the queue
        :rtype: bool
        """
        for event_time in sorted(self.queue.keys()):
            if event_time <= time:
                for event in self.queue.pop(event_time, []):
                    Logger.trace(event_time, "Executing event %s" % (event))
                    if isinstance(event, WindowSizeEvent) or \
                       isinstance(event, LinkBufferSizeEvent):
                        self.graph_events.append(event)
                    event.execute()
            else:
                break
        return len(self.queue) != 0

    def listen(self, component):
        """
        Listens to a network component for events.

        :param component: The component that will dispatch events.
        :type component: EventTarget
        :return: Nothing
        :rtype: None
        """
        component.add_listener(self)
