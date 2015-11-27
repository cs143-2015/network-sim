import matplotlib.pyplot as plt
import os
import time
from events.event_types import WindowSizeEvent, LinkBufferSizeEvent


class Grapher:
    WINDOW_SIZE_NAME = "window_size"
    LINK_BUFFER_NAME = "link_buffer"

    def __init__(self, output_folder=None):
        self.output_folder = output_folder

    def graph_window_size_events(self, graph_events):
        flow_events = self.filter_events(graph_events, WindowSizeEvent)
        # Add graph labels
        self.graph_events(flow_events, "Time (ms)", "Window Size (packets)")
        self.output_current_figure(Grapher.WINDOW_SIZE_NAME)

    def graph_link_buffer_events(self, graph_events):
        link_events = self.filter_events(graph_events, LinkBufferSizeEvent)
        self.graph_events(link_events, "Time (ms)", "# Packets")
        self.output_current_figure(Grapher.LINK_BUFFER_NAME)

    def output_current_figure(self, filename):
        if self.output_folder is not None:
            self.create_output_folder_if_needed()
            filename = "%s/%s-%d.png" % (self.output_folder, filename, time.time())
            plt.savefig(filename)
        else:
            plt.show()

    def create_output_folder_if_needed(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    @staticmethod
    def graph_events(events, xlabel, ylabel):
        """
        Plots the given events with the specified labels

        :param events: Dictionary with flow IDs and a list of events for the ID
        :type events: dict[str, list[GraphEvent]]
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        plt.figure(figsize=(15, 5))
        for id, buffer_sizes in events.items():
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.x_value(), e.y_value()) for e in buffer_sizes])
            plt.plot(x, y, label=("%s" % id))
        # Add legend
        plt.legend(bbox_to_anchor=(1.006, 1), loc=2, borderaxespad=0.)
        # Add graph labels
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    @staticmethod
    def filter_events(graph_events, event_type):
        """
        Filters flow events of the given event type

        :param graph_events: Graph events to filter
        :type graph_events: list[GraphEvent]
        :param event_type: Event type to filter
        :type event_type: class
        :return: Dictionary with flow IDs and a list of events for the ID
        :rtype: dict[str, list[GraphEvent]]
        """
        flow_events = {}
        for event in graph_events:
            if isinstance(event, event_type):
                identifier = event.identifier()
                if identifier not in flow_events:
                    flow_events[identifier] = []
                flow_events[identifier].append(event)
        return flow_events
