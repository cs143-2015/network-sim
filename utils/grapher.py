import matplotlib.pyplot as plt
import os
import time
from events.event_types.graph_events import *

class Grapher:
    WINDOW_SIZE_NAME = "window_size"
    LINK_BUFFER_NAME = "link_buffer"
    DROPPED_PACKETS_NAME = "dropped_packets"
    LINK_THROUGHPUT_NAME = "link_throughput"
    FLOW_THROUGHPUT_NAME = "flow_throughput"

    BUCKET_WIDTH = 75 # In ms

    def __init__(self, output_folder=None):
        self.output_folder = output_folder

    def graph_all(self, graph_events):
        self.graph_window_size_events(graph_events)
        self.graph_link_buffer_events(graph_events)
        self.graph_link_throughput_events(graph_events)
        self.graph_flow_throughput_events(graph_events)
        self.graph_dropped_packets_events(graph_events)

    def graph_window_size_events(self, graph_events):
        flow_events = self.filter_events(graph_events, WindowSizeEvent)
        # Add graph labels
        self.graph_events(flow_events, "Window Size",
                          "Time (ms)", "Window Size (packets)")
        self.output_current_figure(Grapher.WINDOW_SIZE_NAME)

    def graph_link_buffer_events(self, graph_events):
        link_events = self.filter_events(graph_events, LinkBufferSizeEvent)
        link_events = self.make_buckets(link_events)
        self.graph_events_subplots(link_events, "Link Buffer Size",
                                   "Time (ms)", "# Packets")
        self.output_current_figure(Grapher.LINK_BUFFER_NAME)

    def graph_link_throughput_events(self, graph_events):
        link_t_events = self.filter_events(graph_events, LinkThroughputEvent)
        link_t_events = self.make_buckets(link_t_events)
        self.graph_events_subplots(link_t_events, "Link Throughput",
                                   "Time (ms)", "Throughput (Mbps)")
        self.output_current_figure(Grapher.LINK_THROUGHPUT_NAME)

    def graph_flow_throughput_events(self, graph_events):
        flow_t_events = self.filter_events(graph_events, FlowThroughputEvent)
        flow_t_events = self.make_buckets(flow_t_events)
        self.graph_events_subplots(flow_t_events, "Flow Throughput",
                                   "Time (ms)", "Throughput (Mbps)")
        self.output_current_figure(Grapher.FLOW_THROUGHPUT_NAME)

    def graph_dropped_packets_events(self, graph_events):
        d_packets_events = self.filter_events(graph_events, DroppedPacketEvent)
        d_packets_events = self.make_buckets(d_packets_events)
        self.graph_events_bar(d_packets_events, "Dropped Packets",
                              "Time (ms)", "# Packets")
        self.output_current_figure(Grapher.DROPPED_PACKETS_NAME)

    def show(self):
        if self.output_folder is not None:
            return
        else:
            plt.show()

    def output_current_figure(self, filename):
        if self.output_folder is not None:
            self.create_output_folder_if_needed()
            date = time.strftime("%Y-%m_%d-%H_%M_%S")
            filename = "%s/%s-%s.png" % (self.output_folder, filename, date)
            plt.savefig(filename)

    def create_output_folder_if_needed(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    @staticmethod
    def make_buckets(events):
        new_events = {ident: [] for ident in events}
        for ident, event_list in events.items():
            buckets = {}
            for e in event_list:
                bucket_no = int(e.x_value() / Grapher.BUCKET_WIDTH)
                if bucket_no not in buckets:
                    buckets[bucket_no] = []
                buckets[bucket_no].append(e.y_value())
            for bucket_no, bucket in buckets.items():
                bucket_time = bucket_no * Grapher.BUCKET_WIDTH
                bucket_value = sum(bucket) / float(len(bucket))
                new_events[ident].append(BucketEvent(bucket_time, bucket_value))
        return new_events

    @staticmethod
    def graph_events(events, title, xlabel, ylabel):
        """
        Plots the given events with the specified labels with all items in one
        graph.

        :param events: Dictionary with flow IDs and a list of events for the ID
        :type events: dict[str, list[GraphEvent]]
        :param title: Graph title
        :type title: str
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        if len(events) == 0:
            return
        plt.figure(figsize=(15, 5))
        plt.get_current_fig_manager().set_window_title(title)
        plt.title(title)
        for identifier, buffer_sizes in events.items():
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.x_value(), e.y_value()) for e in buffer_sizes])
            plt.plot(x, y, label=("%s" % identifier))
        # Add legend
        plt.legend(bbox_to_anchor=(1.006, 1), loc=2, borderaxespad=0.)
        # Add graph labels
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    @staticmethod
    def graph_events_subplots(events, title, xlabel, ylabel):
        """
        Plots the given events with the specified labels with items in different
        subplots.

        :param events: Dictionary with flow IDs and a list of events for the ID
        :type events: dict[str, list[GraphEvent]]
        :param title: Graph title
        :type title: str
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        if len(events) == 0:
            return
        assert len(events.keys()) <= 9, \
            "Can't put more than 9 subplots on a figure"
        plt.figure(figsize=(15, 10))
        plt.get_current_fig_manager().set_window_title(title)
        i_subplot = 100 * len(events.keys()) + 10 + 1
        for i, (identifier, graph_events) in enumerate(sorted(events.items())):
            plt.subplot(i_subplot)
            plt.autoscale(True)
            i_subplot += 1
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.x_value(), e.y_value()) for e in graph_events])
            plt.plot(x, y)
            # Add the x-label on the last graph
            if len(events) == 1 or i == len(events) - 1:
                plt.xlabel(xlabel)
            # Add the y-label on the middle graph
            if len(events) == 1 or i == (len(events) - 1) / 2:
                plt.ylabel(ylabel)
            plt.title(identifier)
        plt.tight_layout()

    @staticmethod
    def graph_events_bar(events, title, xlabel, ylabel):
        """
        Plots the given events with the specified labels as bar graphs with
        items in different subplots.

        :param events: Dictionary with flow IDs and a list of events for the ID
        :type events: dict[str, list[GraphEvent]]
        :param title: Graph title
        :type title: str
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        if len(events) == 0:
            return
        assert len(events.keys()) <= 9, \
            "Can't put more than 9 subplots on a figure"
        f, subplots = plt.subplots(len(events), 1, figsize=(15, 10))
        plt.get_current_fig_manager().set_window_title(title)
        for i, (identifier, graph_events) in enumerate(sorted(events.items())):
            subplot = subplots[i] if isinstance(subplots, list) else subplots
            # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
            x, y = zip(*[(e.x_value(), e.y_value()) for e in graph_events])
            # Plot the bar graph
            subplot.bar(x, y, width=0.01)
            subplot.set_ylim((0, 2))
            subplot.set_title(identifier)
            # Add the x-label on the last graph
            if len(events) == 1 or i == len(events) - 1:
                subplot.set_xlabel(xlabel)
            # Add the y-label on the middle graph
            if len(events) == 1 or i == (len(events) - 1) / 2:
                subplot.set_ylabel(ylabel)
        plt.tight_layout()

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
