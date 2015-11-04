from components.clock import Clock
from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget


class Network(EventTarget):
    def __init__(self, hosts, routers, links, flows):
        """
        A network instance with flows.

        Args:
            hosts (Host[]):     The list of hosts.
            routers (Router[]): The list of routers.
            links (Link[]):     The list of links.
            flows (Flow[]):     The list of flows.
        """
        super(Network).__init__()
        self.hosts = hosts
        self.routers = routers
        self.links = links
        self.flows = flows

        self.event_queue = EventDispatcher()

        self.clock = Clock()

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        self.clock.start()
        running = True
        while running:
            running = self.event_queue.execute(self.clock.get_time())
