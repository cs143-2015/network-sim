from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget
from utils.grapher import Grapher


class Network(EventTarget):

    # Global program clock
    TIME = None

    def __init__(self, hosts, routers, links, display_graph=True,
                 graph_output=None):
        """
        A network instance with flows.

        Args:
            hosts (Host[]):     The list of hosts.
            routers (Router[]): The list of routers.
            links (Link[]):     The list of links.
        """
        super(Network, self).__init__()
        Network.TIME = 0
        self.hosts = hosts
        self.routers = routers
        self.links = links

        self.event_queue = EventDispatcher()

        for target in self.hosts + self.routers + self.links:
            self.event_queue.listen(target)

        self.running = False

        self.grapher = Grapher(graph_output)
        self.display_graph = display_graph

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        for router in self.routers:
            router.create_routing_table()
        for host in self.hosts:
            host.start_flows()
        try:
            self.running = True
            while self.running:
                self.running = self.event_queue.execute(Network.TIME)
                Network.TIME += 0.001
        except KeyboardInterrupt:
            pass

        if self.display_graph:
            self.grapher.graph_window_size_events(self.event_queue.graph_events)
            self.grapher.graph_link_buffer_events(self.event_queue.graph_events)

    @classmethod
    def get_time(cls):
        """
        Returns the current program time

        :return: Program time
        :rtype: float
        """
        assert cls.TIME is not None, "Start the clock before getting the time."
        return cls.TIME
