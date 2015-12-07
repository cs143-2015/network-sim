import argparse
from utils.grapher import Grapher


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        help="The filenames of the csv file to plot",
                        nargs="*",
                        type=str)
    return parser

if __name__ == '__main__':
    # Parse command line arguments
    args = get_argument_parser().parse_args()
    # Plot the files
    grapher = Grapher()
    for filename in args.filenames:
        grapher.plot_csv(filename)
    # Show the graphs
    grapher.show()
