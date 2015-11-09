from components import Packet, Flow
from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget
from events.event_types import PacketSentEvent


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

        for target in self.hosts + self.routers + self.links:
            self.event_queue.listen(target)

        self.running = False

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
#        flow = Flow("F1", self.hosts[0], self.hosts[1], 4/1024., 0)
#        flow.start()
#        flow2 = Flow("F2", self.hosts[1], self.hosts[0], 4/1024., 0.003)
#        flow2.start()

        try:
            self.running = True
            Network.TIME = 0
            while self.running:
                self.running = self.event_queue.execute(Network.TIME)
                Network.TIME += 0.001
        except KeyboardInterrupt:
            pass

    @classmethod
    def get_time(cls):
        """
        Returns the current program time

        :return: Program time
        :rtype: float
        """
        assert cls.TIME, "Start the clock before getting the time."
        return cls.TIME
