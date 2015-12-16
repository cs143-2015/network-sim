import csv


class CSVProcessor:
    HEADER_DELIMETER = ", "
    CSV_DELIMETER = ','
    CSV_QUOTECHAR = "\""
    CSV_BREAKSTR = 80 * "-" + "\n"

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
            # Write the header with the labels
            h_str = CSVProcessor.string_from_header_dict(header)
            csvfile.write(h_str)
            csv_writer = csv.writer(csvfile,
                                    delimiter=CSVProcessor.CSV_DELIMETER,
                                    quotechar=CSVProcessor.CSV_QUOTECHAR)
            for identifier, values_tuple in data.items():
                # Write the ID in the header
                csvfile.write(CSVProcessor.id_to_header_string(identifier))
                # Write the data itself
                for values in zip(*values_tuple):
                    csv_writer.writerow(values)
                # Add a break string to know we reached the end of the subplot
                csvfile.write(CSVProcessor.CSV_BREAKSTR)

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
            # Get header labels from header line 1
            line = csvfile.readline().strip()
            header_dict = CSVProcessor.header_dict_from_string(line)
            # Get plot data
            data = CSVProcessor.parse_csv_file(csvfile)
        return header_dict, data

    @staticmethod
    def make_header(title, xlabel, ylabel, graph_type):
        """
        Makes a header using the given parameters
        """
        return {"title": title,
                "x-label": xlabel,
                "y-label": ylabel,
                "graph-type": graph_type}

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
    def id_to_header_string(identifier):
        """
        Get the header string for the given identifier
        """
        return "Subplot Identifier: %s\n" % identifier

    @staticmethod
    def id_from_header_string(header_str):
        """
        Get the identifier from the given header string
        """
        if header_str.find(": ") == -1:
            return None
        return header_str.strip().split(": ")[1]

    @staticmethod
    def parse_csv_file(csvfile):
        """
        Parse the given csv file and store the values from the column in a
        dictionary with the keys being the names given

        :param csvfile: File to read
        :type csvfile: FileIO[str]
        :return: Dictionary mapping identifiers to a tuple of two lists of x, y
                 values.
        :rtype: dict[str, (list[float], list[float])]
        """
        data = {}
        # True if the next line is an identifier header, we should start at the
        # part of the file where the first id header is
        is_id_header = True
        for line in csvfile:
            # Whitespace
            if line.strip() == "":
                continue
            # We reached the end of the subplot, set the is_id_header and cont.
            if line.strip() == CSVProcessor.CSV_BREAKSTR.strip():
                is_id_header = True
                continue
            # This line must be an identifier header
            if is_id_header:
                cur_id = CSVProcessor.id_from_header_string(line)
                # Create the empty lists to put the values in
                data[cur_id] = ([], [])
                is_id_header = False  # Next line will be data
                continue
            x, y = line.strip().split(CSVProcessor.CSV_DELIMETER)
            # Put the values in the lists for this identifier
            data[cur_id][0].append(float(x))
            data[cur_id][1].append(float(y))
        return data
