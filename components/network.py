from events import EventTarget, EventDispatcher

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

        self.hosts = hosts
        self.routers = routers
        self.links = links
        self.flows = flows

        self.event_queue = EventDispatcher()

        self.current_time = 0

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        pass
