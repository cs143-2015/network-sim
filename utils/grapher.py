import matplotlib.pyplot as plt
import time
from events.event_types import WindowSizeEvent, LinkBufferSizeEvent


class Grapher:
    WINDOW_SIZE_NAME = "window_size"
    LINK_BUFFER_NAME = "link_buffer"

    def __init__(self, output_folder=None):
        self.output_folder = output_folder

    def graph_window_size_events(self, graph_events):
        flow_events = self.filter_window_size_events(graph_events)
        plt.figure(figsize=(15, 5))
        for flow_id, window_sizes in flow_events.items():
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.time, e.window_size) for e in window_sizes])
            plt.plot(x, y, label=("%s" % flow_id))
        # Add legend
        plt.legend(bbox_to_anchor=(1.006, 1), loc=2, borderaxespad=0.)
        # Add graph labels
        plt.xlabel("Time (ms)")
        plt.ylabel("Window Size (packets)")

        self.output_current_figure(Grapher.WINDOW_SIZE_NAME)

    def graph_link_buffer_events(self, graph_events):
        link_events = self.filter_link_buffer_size_events(graph_events)
        plt.figure(figsize=(15, 5))
        for link_id, buffer_sizes in link_events.items():
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.time, e.buffer_size) for e in buffer_sizes])
            plt.plot(x, y, label=("%s" % link_id))
        # Add legend
        plt.legend(bbox_to_anchor=(1.006, 1), loc=2, borderaxespad=0.)
        # Add graph labels
        plt.xlabel("Time (ms)")
        plt.ylabel("# Packets")

        self.output_current_figure(Grapher.LINK_BUFFER_NAME)

    def output_current_figure(self, filename):
        if self.output_folder is not None:
            filename = "%s/%s-%d.png" % (self.output_folder, filename, time.time())
            plt.savefig(filename)
        else:
            plt.show()

    @staticmethod
    def filter_window_size_events(graph_events):
        flow_events = {}
        for event in graph_events:
            if isinstance(event, WindowSizeEvent):
                if event.flow_id not in flow_events:
                    flow_events[event.flow_id] = []
                flow_events[event.flow_id].append(event)
        return flow_events

    @staticmethod
    def filter_link_buffer_size_events(graph_events):
        link_events = {}
        for event in graph_events:
            if isinstance(event, LinkBufferSizeEvent):
                if event.link_id not in link_events:
                    link_events[event.link_id] = []
                link_events[event.link_id].append(event)
        return link_events
