import threading


class Clock:
    """
    Asynchronous program clock
    """

    def __init__(self, start_time=0, increments=0.1, increment_interval=0.0000001):
        """
        Initializes program clock

        :param start_time: Start time for the clock
        :type start_time: int
        :param increments: Increment added at every increment interval
        :type increments: int
        :param increment_interval: Time in seconds between increments
        :type increment_interval: int
        :return: Clock instance
        :rtype: Clock
        """
        self.time = start_time
        self.increments = increments
        self.increment_interval = increment_interval
        self.running = True

    def start(self):
        """
        Begin running the clock asynchronously

        :return: Nothing
        :rtype: None
        """
        self.running = True
        self.run()

    def stop(self):
        """
        Stop running the clock

        :return: Nothing
        :rtype: None
        """
        self.running = False

    def run(self):
        """
        Increment the timer at every increment interval.

        :return: Nothing
        :rtype: None
        """
        if not self.running:
            return
        self.time += self.increments
        threading.Timer(self.increment_interval, self.run).start()

    def get_time(self):
        """
        Get the current program time

        :return: Time
        :rtype: int
        """
        return self.time
