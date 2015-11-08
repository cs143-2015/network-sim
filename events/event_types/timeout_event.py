from events.event_types.event import Event


class TimeoutEvent(Event):

    # Default timeout period
    TIMEOUT_PERIOD = 100

    def __init__(self, time, host, packet_id):

        super(TimeoutEvent, self).__init__(time)
        self.host = host
        self.packet_id = packet_id

    def execute(self):
        self.host.resend_if_necessary(self.packet_id, self.time)

    def __repr__(self):
        return "TimeoutEvent<%s : %s>" % (self.host, self.packet_id)
