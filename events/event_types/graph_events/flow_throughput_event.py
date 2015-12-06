from graph_event import GraphEvent


class FlowThroughputEvent(GraphEvent):
    def __init__(self, time, flow_id, flow_throughput):
        super(FlowThroughputEvent, self).__init__(time)
        self.flowId = flow_id
        self.flowThroughput = flow_throughput

    def __repr__(self):
        return "FlowThroughputEvent<%s : %.2f>" \
               % (self.flowId, self.flowThroughput)

    def identifier(self):
        return self.flowId

    def y_value(self):
        """
        Flow throughput.

        :return: Link throughput in Mbps
        :rtype: float
        """
        return self.flowThroughput / 1e6
