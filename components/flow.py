class Flow:
    def __init__(self, id, src, dest, amount, start):
        """
        A network flow.

        Args:
            id (str):       The name of the flow.
            src (Host):     The source host.
            dest (Host):    The destination host.
            amount (int):   The amount of data to send, in MB.
            start (float):  The time at which the flow starts, in s.
        """
        self.id = id
        self.src = src
        self.dest = dest
        self.amount = amount
        self.start = start
