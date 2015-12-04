from event import Event
from utils import Logger


class UpdateDynamicRoutingTableEvent(Event):
    def __init__(self, time, router):
        super(UpdateDynamicRoutingTableEvent, self).__init__(time)
        self.router = router

    def execute(self):
        Logger.debug(self.time, "%s: Updating dynamic routing table." % self)
        self.router.create_routing_table(dynamic=True)

    def __repr__(self):
        return "UpdateDynamicRoutingTableEvent<%s>" % self.router
