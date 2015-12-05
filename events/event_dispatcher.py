from collections import namedtuple

from events.event_types.event import Event
from events.event_types.graph_events import GraphEvent
from utils import Logger

TimerTuple = namedtuple("TimerTuple", ["interval", "event"])

class EventDispatcher:

    def __init__(self):
        """
        An event queue that process events at a specific time.
        """
        # Queue containing events to dispatch, keys are dispatch times
        self.queue = {}
        # Timer queue containing timers to dispatch, keys are dispatch times
        self.timers = {}
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
            self.queue[time] = [event]

    def execute(self, time):
        """
        Executes all events that were to be dispatched by the current time.

        :param time: The current time.
        :type time: int
        :return: True if there are still events left in the queue
        :rtype: bool
        """
        # Execute events
        for event_time in sorted(self.queue.keys()):
            if event_time <= time:
                for event in self.queue.pop(event_time, []):
                    Logger.trace(event_time, "Executing event %s" % event)
                    if isinstance(event, GraphEvent):
                        self.graph_events.append(event)
                    event.execute()
            else:
                break
        # Execute timers
        for timer_time in sorted(self.timers.keys()):
            if timer_time <= time:
                for timer_tuple in self.timers.pop(timer_time):
                    # Get the event and execute it
                    event = timer_tuple.event
                    interval = timer_tuple.interval
                    event.time = time
                    event.execute()
                    # Put the timer back on the queue with the next exec time
                    self.add_timer(event, time, interval)
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

    def add_timer(self, event, time, interval):
        """
        Execute the given event periodically with the given time interval.
        Does not execute the timer if there are no more events

        :param event: Event to execute
        :type event: Event
        :param time: Time when the timer was added
        :type time: float
        :param interval: Time interval between timer executions
        :type interval: float
        :return: Nothing
        :rtype: None
        """
        assert interval >= 0.001, \
            "Can't execute a timer in smaller interval than the increments."
        time += interval
        if time in self.timers:
            self.timers[time].append(TimerTuple(interval, event))
        else:
            self.timers[time] = [TimerTuple(interval, event)]
