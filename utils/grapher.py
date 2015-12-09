import matplotlib.pyplot as plt
import os
import time
from numpy import ndarray

from events.event_types.graph_events import *
from csv_processor import CSVProcessor


class Grapher:
    WINDOW_SIZE_NAME = "window_size"
    LINK_BUFFER_NAME = "link_buffer"
    DROPPED_PACKETS_NAME = "dropped_packets"
    LINK_THROUGHPUT_NAME = "link_throughput"
    FLOW_THROUGHPUT_NAME = "flow_throughput"

    BUCKET_WIDTH = 75  # In ms

    def __init__(self, output_folder=None):
        self.outputFolder = output_folder
        self.csvProcessor = CSVProcessor()
        self.timeStr = time.strftime("%Y-%m_%d-%H_%M_%S")

    def graph_all(self, graph_events):
        self.graph_window_size_events(graph_events)
        self.graph_link_buffer_events(graph_events)
        self.graph_link_throughput_events(graph_events)
        self.graph_flow_throughput_events(graph_events)
        self.graph_dropped_packets_events(graph_events)

    def graph_window_size_events(self, graph_events):
        flow_events = self.filter_events(graph_events, WindowSizeEvent)
        if len(flow_events) == 0: return
        header_strs = ["Window Size", "Time (ms)", "Window Size (packets)"]
        self.graph_events_subplots(flow_events, *header_strs)
        self.output_current_figure(Grapher.WINDOW_SIZE_NAME)
        header_strs.append("Subplot")
        self.output_csv(Grapher.WINDOW_SIZE_NAME, flow_events, header_strs)

    def graph_link_buffer_events(self, graph_events):
        link_events = self.filter_events(graph_events, LinkBufferSizeEvent)
        if len(link_events) == 0: return
        link_events = self.make_buckets_events(link_events)
        header_strs = ["Link Buffer Size", "Time (ms)", "# Packets"]
        self.graph_events_subplots(link_events, *header_strs)
        self.output_current_figure(Grapher.LINK_BUFFER_NAME)
        header_strs.append("Subplot")
        self.output_csv(Grapher.LINK_BUFFER_NAME, link_events, header_strs)

    def graph_link_throughput_events(self, graph_events):
        link_t_events = self.filter_events(graph_events, LinkThroughputEvent)
        if len(link_t_events) == 0: return
        link_t_events = self.make_buckets_events(link_t_events)
        header_strs = ["Link Throughput", "Time (ms)", "Throughput (Mbps)"]
        self.graph_events_subplots(link_t_events, *header_strs)
        self.output_current_figure(Grapher.LINK_THROUGHPUT_NAME)
        header_strs.append("Subplot")
        self.output_csv(Grapher.LINK_THROUGHPUT_NAME, link_t_events, header_strs)

    def graph_flow_throughput_events(self, graph_events):
        flow_t_events = self.filter_events(graph_events, FlowThroughputEvent)
        if len(flow_t_events) == 0: return
        flow_t_events = self.make_buckets_events(flow_t_events)
        header_strs = ["Flow Throughput", "Time (ms)", "Throughput (Mbps)"]
        self.graph_events_subplots(flow_t_events, *header_strs)
        self.output_current_figure(Grapher.FLOW_THROUGHPUT_NAME)
        header_strs.append("Subplot")
        self.output_csv(Grapher.FLOW_THROUGHPUT_NAME, flow_t_events, header_strs)

    def graph_dropped_packets_events(self, graph_events):
        d_packets_events = self.filter_events(graph_events, DroppedPacketEvent)
        if len(d_packets_events) == 0: return
        d_packets_events = self.make_buckets_events(d_packets_events)
        header_strs = ["Dropped Packets", "Time (ms)", "# Packets"]
        self.graph_events_bar(d_packets_events, *header_strs)
        self.output_current_figure(Grapher.DROPPED_PACKETS_NAME)
        header_strs.append("Bar")
        self.output_csv(Grapher.DROPPED_PACKETS_NAME, d_packets_events, header_strs)

    def show(self):
        plt.show()

    def output_current_figure(self, filename):
        if self.outputFolder is None:
            return
        self.create_output_folder_if_needed()
        filename = "%s/%s-%s.png" % (self.outputFolder, filename, self.timeStr)
        plt.savefig(filename)

    def output_csv(self, filename, graph_events, header_strs):
        """
        Output the graph events to a csv file

        :param filename: Filename prefix for the csv file
        :type filename: str
        :param graph_events: Graph events to output data for
        :type graph_events: dict[str, list[GraphEvents]]
        :param header_strs: [title, x-label, y-label, graph-type]
        :type header_strs: list[str]
        :return: Nothing
        :rtype: None
        """
        if self.outputFolder is None or len(graph_events) == 0:
            return
        self.create_output_folder_if_needed()
        title, xlabel, ylabel, graph_type = header_strs
        header = CSVProcessor.make_header(title, xlabel, ylabel, graph_type)
        filename = "%s/%s-%s.csv" % (self.outputFolder, filename, self.timeStr)
        data = self.dict_from_events(graph_events)
        CSVProcessor.output_csv(filename, data, header)

    def plot_csv(self, filename, bucket_width):
        """
        Read the csv file with the given filename and plot the data

        :param filename: Filename of the csv file
        :type filename: str
        :param bucket_width: Bucket size to use for the graphs
        :type bucket_width: int
        :return: Nothing
        :rtype: None
        """
        header_dict, data = CSVProcessor.data_from_csv_file(filename)
        data = self.make_buckets_data(data, bucket_width)
        if header_dict["graph-type"] == "Subplot":
            graph_fn = self.graph_events_subplots \
                if bucket_width else self.graph_data_subplots
        elif header_dict["graph-type"] == "Bar":
            graph_fn = self.graph_events_bar \
                if bucket_width else self.graph_data_bar
        elif header_dict["graph-type"] == "Overlay":
            graph_fn = self.graph_events_overlay \
                if bucket_width else self.graph_data_overlay
        else:
            raise ValueError("Unhandled graph type.")
        graph_fn(data,
                 header_dict["title"],
                 header_dict["x-label"],
                 header_dict["y-label"])

    def create_output_folder_if_needed(self):
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)

    @staticmethod
    def make_buckets_events(events):
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
    def make_buckets_data(data, bucket_width):
        new_data = {identifier: [] for identifier in data}
        for ident, values_tuple in data.items():
            buckets = {}
            for x, y in data:
                bucket_no = int(x / bucket_width)
                if bucket_no not in buckets:
                    buckets[bucket_no] = []
                    buckets[bucket_no].append(y)
            for bucket_no, bucket in buckets.items():
                bucket_time = bucket_no * bucket_width
                bucket_val = sum(bucket) / float(len(bucket))
                new_data[ident].append(BucketEvent(bucket_time, bucket_val))
        return new_data

    @staticmethod
    def graph_events_overlay(events, title, xlabel, ylabel):
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
        data = Grapher.dict_from_events(events)
        Grapher.graph_data_overlay(data, title, xlabel, ylabel)

    @staticmethod
    def graph_data_overlay(data, title, xlabel, ylabel):
        """
        Plots the given data with the specified labels with all items in one
        graph.

        :param data: Mapping of flow IDs to a tuple with a list of x, y values
        :type data: dict[str, (list[float], list[float])]
        :param title: Graph title
        :type title: str
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        if len(data) == 0:
            return
        plt.figure(figsize=(15, 5))
        plt.get_current_fig_manager().set_window_title(title)
        plt.title(title)
        for identifier, plot_tuple in data.items():
            x, y = plot_tuple
            plt.plot(x, y, label=("%s" % identifier))
        # Add legend
        plt.legend(bbox_to_anchor=(1.006, 1), loc=2, borderaxespad=0.)
        # Add graph labels
        plt.title(title)
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
        data = Grapher.dict_from_events(events)
        Grapher.graph_data_subplots(data, title, xlabel, ylabel)

    @staticmethod
    def graph_data_subplots(data, title, xlabel, ylabel):
        """
        Plots the given data with the specified labels with items in different
        subplots.

        :param data: Mapping of flow IDs to a tuple with a list of x, y values
        :type data: dict[str, (list[float], list[float])]
        :param title: Graph title
        :type title: str
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        if len(data) == 0:
            return
        assert len(data.keys()) <= 9, \
            "Can't put more than 9 subplots on a figure"
        plt.figure(figsize=(15, 10))
        plt.get_current_fig_manager().set_window_title(title)
        i_subplot = 100 * len(data.keys()) + 10 + 1
        for i, (identifier, plot_tuple) in enumerate(sorted(data.items())):
            plt.subplot(i_subplot)
            plt.autoscale(True)
            i_subplot += 1
            x, y = plot_tuple
            plt.plot(x, y)
            # Add the x-label on the last graph
            if len(data) == 1 or i == len(data) - 1:
                plt.xlabel(xlabel)
            # Add the y-label on the middle graph
            if len(data) == 1 or i == (len(data) - 1) / 2:
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
        data = Grapher.dict_from_events(events)
        Grapher.graph_data_bar(data, title, xlabel, ylabel)

    @staticmethod
    def graph_data_bar(data, title, xlabel, ylabel):
        """
        Plots the given data with the specified labels as bar graphs with
        items in different subplots.

        :param data: Mapping of flow IDs to a tuple with a list of x, y values
        :type data: dict[str, (list[float], list[float])]
        :param title: Graph title
        :type title: str
        :param xlabel: X-label to add to the graph
        :type xlabel: str
        :param ylabel: Y-label to add to the graph
        :type ylabel: str
        :return: Nothing
        :rtype: None
        """
        if len(data) == 0:
            return
        assert len(data.keys()) <= 9, \
            "Can't put more than 9 subplots on a figure"
        f, subplots = plt.subplots(len(data), 1, figsize=(15, 10))
        plt.get_current_fig_manager().set_window_title(title)
        for i, (identifier, plot_tuple) in enumerate(sorted(data.items())):
            subplot = subplots[i] if isinstance(subplots, ndarray) else subplots
            x, y = plot_tuple
            # Plot the bar graph
            subplot.bar(x, y, width=0.01)
            subplot.set_ylim((0, 2))
            subplot.set_title(identifier)
            # Add the x-label on the last graph
            if len(data) == 1 or i == len(data) - 1:
                subplot.set_xlabel(xlabel)
            # Add the y-label on the middle graph
            if len(data) == 1 or i == (len(data) - 1) / 2:
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
        filtered_events = {}
        for event in graph_events:
            if isinstance(event, event_type):
                identifier = event.identifier()
                if identifier not in filtered_events:
                    filtered_events[identifier] = []
                filtered_events[identifier].append(event)
        return filtered_events

    @staticmethod
    def values_from_events(graph_events):
        """
        Gets the x and y values form the graph events

        :param graph_events: Graph events to get values from
        :type graph_events: list[GraphEvents]
        :return: Tuple containing two lists of x and y values respectively
        :rtype: (list[float], list[float])
        """
        # zip(*lst) swaps axes; (x1, y1), (x2, y2) -> (x1, x2), (y1, y2)
        return zip(*[(e.x_value(), e.y_value()) for e in graph_events])

    @staticmethod
    def dict_from_events(ids_events_dict):
        """
        Gets a dictionary mapping subplot identifiers to a tuple with two
        lists of x and y values

        :param ids_events_dict: Dictionary mapping IDs to events for ID
        :type ids_events_dict: dict[str, GraphEvents]
        :return: Dictionary mapping IDs to a tuple with lists of x and y values
        :rtype: dict[str, (list[float], list[float])]
        """
        events = {}
        for (identifier, graph_events) in ids_events_dict.items():
            events[identifier] = Grapher.values_from_events(graph_events)
        return events
