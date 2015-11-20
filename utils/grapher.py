import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from events.event_types import WindowSizeEvent


class Grapher:
    def __init__(self, output_file=None):
        self.outputFilename = output_file

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

        if self.outputFilename is not None:
            plt.savefig(self.outputFilename)
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
