import csv
from itertools import izip_longest, chain
from operator import is_not
from functools import partial


class CSVProcessor:
    HEADER_DELIMETER = ", "
    CSV_DELIMETER = ','
    CSV_QUOTECHAR = "\""

    @staticmethod
    def output_csv(filename, data, header):
        """
        Outputs the given data with the specified header to the file with the
        given filename

        :param filename: Filename of the output file
        :type filename: str
        :param data: Map of event identifiers to a tuple with x and y values
        :type data: dict[str, (list[float], list[float])]
        :param header: Header dictionary with values to write
        :type header: dict[str, str]
        :return: Nothing
        :rtype: None
        """
        with open(filename, 'wb') as csvfile:
            ids, csv_values = CSVProcessor.processed_csv_values(data)
            csv_writer = csv.writer(csvfile,
                                    delimiter=CSVProcessor.CSV_DELIMETER,
                                    quotechar=CSVProcessor.CSV_QUOTECHAR)
            # Write the header with the header data and identifiers
            h_str = CSVProcessor.string_from_header_dict(header)
            csvfile.write(h_str)
            csv_writer.writerow(ids)
            # Write the values
            csv_writer.writerows(csv_values)

    @staticmethod
    def data_from_csv_file(filename):
        """
        Extract the data from the given csv file

        :param filename: Filename of the csv file
        :type filename: str
        :return: Header dictionary and dictionary of identifier -> data
        :rtype: (dict[str, str], dict[str, (list[float], list[float])])
        """
        # Read the csv header
        with open(filename, "r") as csvfile:
            # Get header dictionary from header line 1
            line = csvfile.readline().strip()
            header_dict = CSVProcessor.header_dict_from_string(line)
            # Get ordered identifiers from header line 2
            line = csvfile.readline().strip()
            ids = list(line.split(CSVProcessor.CSV_DELIMETER))
            names = [("x" + str(i), "y" + str(i)) for i in range(0, len(ids))]
            names = list(chain.from_iterable(names))
            # Get plot data
            data = CSVProcessor.parse_csv_file(csvfile, names)
            id_data_map = {}
            for i, identifier in enumerate(ids):
                id_data_map[identifier] = (data["x%d" % i], data["y%d" % i])
        return header_dict, id_data_map

    @staticmethod
    def make_header(title, xlabel, ylabel, is_bar):
        """
        Makes a header using the given parameters
        """
        return {"title": title,
                "x-label": xlabel,
                "y-label": ylabel,
                "graph-type": "Bar" if is_bar else "Plot"}

    @staticmethod
    def string_from_header_dict(header):
        """
        Get the header string from the given header dictionary

        :param header: Header dictionary with labels names as keys
        :type header: dict[str, str]
        :return: Header string
        :rtype: str
        """
        return "title: %s, x-label: %s, y-label: %s, graph-type: %s\n" % \
               (header["title"], header["x-label"], header["y-label"],
                header["graph-type"])

    @staticmethod
    def header_dict_from_string(string):
        """
        Get the header dictionary from the given string
        """
        header_dict = {}
        for header_string in string.split(CSVProcessor.HEADER_DELIMETER):
            key, value = header_string.split(": ")
            header_dict[key] = value
        return header_dict

    @staticmethod
    def parse_csv_file(csvfile, names):
        """
        Parse the given csv file and store the values from the column in a
        dictionary with the keys being the names given

        :param csvfile: File to read
        :type csvfile: FileIO[str]
        :param names: list of x0, y0, ... for the columns
        :type names: list[str]
        :return: Dictionary with the given names and the values for those names
        :rtype: dict[str, list[float]]
        """
        plot_values = {}
        for name in names:
            plot_values[name] = []
        for line in csvfile:
            for i, value in enumerate(line.strip().split(CSVProcessor.CSV_DELIMETER)):
                # x values come before y so they'll be at the even # columns
                if i % 2 == 0:
                    name = "x%d" % (i / 2)
                    plot_values[name].append(float(value))
                # y values will be at the odd # columns
                else:
                    name = "y%d" % ((i - 1) / 2)
                    plot_values[name].append(float(value))
        return plot_values

    @staticmethod
    def processed_csv_values(ids_data_dict):
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

        :param ids_data_dict: Dictionary mapping IDs to events for ID
        :type ids_data_dict: dict[str, (list(float), list(float))]
        :return: Tuple of with a list ordered according to how the ID values
                 are stored and the list of the tuple values
        :rtype: (list[str], list[(float, float, ...)])
        """
        # Get a tuple of the identifiers and the values, insert the values into
        # a dictionary with list lengths as keys (in order to later sort them)
        values = {}
        for identifier, values_tuple in ids_data_dict.items():
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
        zipped_values = [tuple(filter(partial(is_not, None), val)) for val in zipped_values]
        # Filter any empty tuples
        zipped_values = filter(None, zipped_values)
        return ordered_ids, zipped_values
