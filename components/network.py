from components.clock import Clock
from components import Packet
from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget
from events.event_types import PacketSentEvent


class Network(EventTarget):

    # Global program clock
    CLOCK = None

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
        Network.CLOCK = Clock()

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        self.CLOCK.start()
        try:
            self.running = True
            while self.running:
                self.running = self.event_queue.execute(self.CLOCK.get_time())
        except KeyboardInterrupt:
            pass
        self.CLOCK.stop()

    @staticmethod
    def get_time():
        """
        Returns the current program time

        :return: Program time
        :rtype: int
        """
        assert Network.CLOCK, "Start the clock before getting the time."
        return Network.CLOCK.get_time()
