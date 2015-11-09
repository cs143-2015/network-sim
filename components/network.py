from components import Packet, Flow
from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget
from events.event_types import PacketSentEvent, WindowSizeEvent


class Network(EventTarget):

    # Global program clock
    TIME = None

    def __init__(self, hosts, routers, links, flows):
        """
        A network instance with flows.

        Args:
            hosts (Host[]):     The list of hosts.
            routers (Router[]): The list of routers.
            links (Link[]):     The list of links.
            flows (Flow[]):     The list of flows.
        """
        super(Network, self).__init__()
        self.hosts = hosts
        self.routers = routers
        self.links = links
        self.flows = flows

        self.event_queue = EventDispatcher()

        for target in self.hosts + self.routers + self.links + self.flows:
            self.event_queue.listen(target)

        self.running = False

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        for flow in self.flows:
            flow.start()

        try:
            self.running = True
            Network.TIME = 0
            while self.running:
                self.running = self.event_queue.execute(Network.TIME)
                Network.TIME += 0.001
        except KeyboardInterrupt:
            pass

        self.graph()

    def graph(self):
        import matplotlib.pyplot as plt
        flow_events = {}
        for event in self.event_queue.graph_events:
            if isinstance(event, WindowSizeEvent):
                if event.flow_id not in flow_events:
                    flow_events[event.flow_id] = []
                flow_events[event.flow_id].append(event)
        plt.figure(figsize=(15,3))
        for flow_id, window_sizes in flow_events.items():
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.time, e.window_size) for e in window_sizes])
            plt.plot(x, y)
        plt.show()

    @classmethod
    def get_time(cls):
        """
        Returns the current program time

        :return: Program time
        :rtype: float
        """
        assert cls.TIME, "Start the clock before getting the time."
        return cls.TIME
