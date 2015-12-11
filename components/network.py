from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget
from utils.grapher import Grapher
from utils.graphing_helpers import get_flow_throughput_events


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
            display_graph(bool) Whether we should display the graph when done
            graph_output(str)   Output folder if data needs saving
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
        self.displayGraph = display_graph

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        for router in self.routers:
            router.create_routing_table()
        for host in self.hosts:
            host.start_flow()

        self._run()
        
        self.create_graphs()
        if self.displayGraph:
            self.display_graphs()

    def _run(self):
        """
        Begin running the network until done or a KeyboardInterrupt is received
        """
        try:
            self.running = True
            while self.running:
                self.running = self.event_queue.execute(Network.TIME)
                Network.TIME += 0.001
        except KeyboardInterrupt:
            pass

    def create_graphs(self):
        """
        Handle graph events processing and graphing
        """
        graph_events = self.event_queue.graph_events
        p_received_events = self.event_queue.packet_received_events
        # Add the flow throughput events to the graph events
        graph_events += get_flow_throughput_events(p_received_events)
        self.grapher.graph_all(self.event_queue.graph_events)        

    def display_graphs(self):
        """
        Handle showing the graphs
        """
        self.grapher.show()

    @classmethod
    def get_time(cls):
        """
        Returns the current program time

        :return: Program time
        :rtype: float
        """
        assert cls.TIME is not None, "Start the clock before getting the time."
        return cls.TIME
