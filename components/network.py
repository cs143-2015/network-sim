from components.clock import Clock
from components import Packet
from events.event_dispatcher import EventDispatcher
from events.event_target import EventTarget
from events.event_types import PacketSentEvent


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
        super(Network, self).__init__()
        self.hosts = hosts
        self.routers = routers
        self.links = links
        self.flows = flows

        self.event_queue = EventDispatcher()

        for target in self.hosts + self.routers + self.links:
            self.event_queue.listen(target)

        self.clock = Clock()

    def run(self):
        """
        Starts the event dispatcher and begins running the clock.
        """
        # Fake flow stuff
        flow_packet = Packet([1 for i in range(Packet.FLOW_PACKET_SIZE)], self.hosts[0], self.hosts[1])
        self.event_queue.push(PacketSentEvent(0, flow_packet, self.links[0], self.hosts[1]))

        # Real code starts here
        self.clock.start()
        try:
            running = True
            while running:
                running = self.event_queue.execute(self.clock.get_time())
        except KeyboardInterrupt:
            pass
        self.clock.stop()
