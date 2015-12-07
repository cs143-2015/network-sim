from graph_event import GraphEvent


class BucketEvent(GraphEvent):
    def __init__(self, time, value):
        super(GraphEvent, self).__init__(time)
        self.value = value

    def __repr__(self):
        return "BucketEvent<%s : %.3f>" % (self.time, self.value)

    def identifier(self):
        return self.time

    def y_value(self):
        return self.value
