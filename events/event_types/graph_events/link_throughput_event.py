from graph_event import GraphEvent


class LinkThroughputEvent(GraphEvent):
    def __init__(self, time, link_id, link_throughput):
        super(LinkThroughputEvent, self).__init__(time)
        self.linkId = link_id
        self.linkThroughput = link_throughput

    def __repr__(self):
        return "LinkThroughputEvent<%s : %.2f>" \
               % (self.linkId, self.linkThroughput)

    def identifier(self):
        return self.linkId

    def y_value(self):
        """
        Link throughput.

        :return: Link throughput in bits / s
        :rtype: float
        """
        return self.linkThroughput
