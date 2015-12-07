import csv
import matplotlib.pyplot as plt
import os
import time
from itertools import izip_longest

from events.event_types.graph_events import *


class Grapher:
    WINDOW_SIZE_NAME = "window_size"
    LINK_BUFFER_NAME = "link_buffer"
    DROPPED_PACKETS_NAME = "dropped_packets"
    LINK_THROUGHPUT_NAME = "link_throughput"
    FLOW_THROUGHPUT_NAME = "flow_throughput"

    BUCKET_WIDTH = 75  # In ms

    CSV_DELIMETER = ','
    CSV_QUOTECHAR = "\""

    def __init__(self, output_folder=None):
        self.outputFolder = output_folder
        self.timeStr = time.strftime("%Y-%m_%d-%H_%M_%S")

    def graph_all(self, graph_events):
        self.graph_window_size_events(graph_events)
        self.graph_link_buffer_events(graph_events)
        self.graph_link_throughput_events(graph_events)
        self.graph_flow_throughput_events(graph_events)
        self.graph_dropped_packets_events(graph_events)

    def graph_window_size_events(self, graph_events):
        flow_events = self.filter_events(graph_events, WindowSizeEvent)
        header_strs = ["Window Size", "Time (ms)", "Window Size (packets)"]
        self.graph_events(flow_events, *header_strs)
        self.output_current_figure(Grapher.WINDOW_SIZE_NAME)
        header = self.make_header(*header_strs)
        self.output_csv(Grapher.WINDOW_SIZE_NAME, flow_events, header)

    def graph_link_buffer_events(self, graph_events):
        link_events = self.filter_events(graph_events, LinkBufferSizeEvent)
        link_events = self.make_buckets(link_events)
        header_strs =  ["Link Buffer Size", "Time (ms)", "# Packets"]
        self.graph_events_subplots(link_events, *header_strs)
        self.output_current_figure(Grapher.LINK_BUFFER_NAME)
        header = self.make_header(*header_strs)
        self.output_csv(Grapher.LINK_BUFFER_NAME, link_events, header)

    def graph_link_throughput_events(self, graph_events):
        link_t_events = self.filter_events(graph_events, LinkThroughputEvent)
        link_t_events = self.make_buckets(link_t_events)
        header_strs = ["Link Throughput", "Time (ms)", "Throughput (Mbps)"]
        self.graph_events_subplots(link_t_events, *header_strs)
        self.output_current_figure(Grapher.LINK_THROUGHPUT_NAME)
        header = self.make_header(*header_strs)
        self.output_csv(Grapher.LINK_THROUGHPUT_NAME, link_t_events, header)

    def graph_flow_throughput_events(self, graph_events):
        flow_t_events = self.filter_events(graph_events, FlowThroughputEvent)
        flow_t_events = self.make_buckets(flow_t_events)
        header_strs = ["Flow Throughput", "Time (ms)", "Throughput (Mbps)"]
        self.graph_events_subplots(flow_t_events, *header_strs)
        self.output_current_figure(Grapher.FLOW_THROUGHPUT_NAME)
        header = self.make_header(*header_strs)
        self.output_csv(Grapher.FLOW_THROUGHPUT_NAME, flow_t_events, header)

    def graph_dropped_packets_events(self, graph_events):
        d_packets_events = self.filter_events(graph_events, DroppedPacketEvent)
        d_packets_events = self.make_buckets(d_packets_events)
        header_strs = ["Dropped Packets", "Time (ms)", "# Packets"]
        self.graph_events_bar(d_packets_events, *header_strs)
        self.output_current_figure(Grapher.DROPPED_PACKETS_NAME)
        header = self.make_header(*header_strs)
        self.output_csv(Grapher.DROPPED_PACKETS_NAME, d_packets_events, header)

    def show(self):
        plt.show()

    def output_current_figure(self, filename):
        if self.outputFolder is None:
            return
        self.create_output_folder_if_needed()
        filename = "%s/%s-%s.png" % (self.outputFolder, filename, self.timeStr)
        plt.savefig(filename)

    def output_csv(self, filename, graph_events, header):
        if self.outputFolder is None or len(graph_events) == 0:
            return
        self.create_output_folder_if_needed()
        import pytest;pytest.set_trace()
        filename = "%s/%s-%s.csv" % (self.outputFolder, filename, self.timeStr)
        with open(filename, 'wb') as csvfile:
            ids, csv_values = self.processed_csv_values(graph_events)
            csv_writer = csv.writer(csvfile, delimiter=self.CSV_DELIMETER,
                                    quotechar=self.CSV_QUOTECHAR)
            # Write the header with the header data and identifiers
            h_str = self.string_from_header_dict(header)
            csvfile.write(h_str)
            csv_writer.writerow(ids)
            # Write the values
            csv_writer.writerows(csv_values)

    def create_output_folder_if_needed(self):
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)

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
        for identifier, graph_events in events.items():
            x, y = Grapher.values_from_events(graph_events)
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
            x, y = Grapher.values_from_events(graph_events)
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
            x, y = Grapher.values_from_events(graph_events)
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

    @staticmethod
    def make_header(title, xlabel, ylabel):
        """
        Makes a header using the given parameters
        """
        return {"title": title, "x-label": xlabel, "y-label": ylabel}

    @staticmethod
    def string_from_header_dict(header):
        """
        Get the header string from the given header dictionary

        :param header: Header dictionary with labels names as keys
        :type header: dict[str, str]
        :return: Header string
        :rtype: str
        """
        return "title: %s, x-label: %s, y-label: %s\n" % \
               (header["title"], header["x-label"], header["y-label"])

    @staticmethod
    def processed_csv_values(ids_events_dict):
        """
        Creates a list of tuples with the given graph events. The plot data
        tuples will be ordered with the ones having the most rows first to
        be able to write them to the csv as follows:
        x11, y11, x21, y21
        x12, y12, x22, y22
        ..., ..., ..., ...,
        x17, y17, x27, y27
        x18, y18
        x19, y19

        :param ids_events_dict: Dictionary mapping IDs to events for ID
        :type ids_events_dict: dict[str, GraphEvents]
        :return: Tuple of with a list ordered according to how the ID values
                 are stored and the list of the tuple values
        :rtype: (list[str], list[(float, float, ...)])
        """
        # Get a tuple of the identifiers and the values, insert the values into
        # a dictionary with list lengths as keys (in order to later sort them)
        values = {}
        for identifier, values_tuple in Grapher.dict_from_events(ids_events_dict).items():
            x_values, y_values = values_tuple
            values[len(x_values)] = (identifier, x_values, y_values)
        # Store the sorted tuples with the pairs having the most rows first
        sorted_values = []
        ordered_ids = []
        for _, t in sorted(values.items()):
            ordered_ids.append(t[0])
            sorted_values.append(t[1])
            sorted_values.append(t[2])
        # Zip all the lists into tuples that are None-padded at the ends
        zipped_values = izip_longest(*sorted_values)
        # Filter the None values to simply write the values
        zipped_values = [tuple(filter(None, val)) for val in zipped_values]
        # Filter any empty tuples
        zipped_values = filter(None, zipped_values)
        return ordered_ids, zipped_values
