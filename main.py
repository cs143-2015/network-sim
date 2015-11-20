import argparse

from utils import Logger, LoggerLevel, Parser
from components import Network


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_spec",
                        help="the XML file describing the flow specification",
                        type=str)
    parser.add_argument("-l", "--log",
                        help="the level at which to log information.",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="INFO")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-G", "--no-graph",
                       help="do not graph at the end of the simulation",
                       action="store_false", dest="graph")
    group.add_argument("-o", "--output",
                       help="the file to output the graph to",
                       type=str)
    return parser

if __name__ == '__main__':
    # Parse command line arguments
    args = get_argument_parser().parse_args()
    # Set logger print level
    Logger.PRINT_LEVEL = LoggerLevel.__dict__[args.log]
    # Parse XML file
    hosts, routers, links, flows = Parser(args.flow_spec).parse()
    # Create and run network
    network = Network(hosts, routers, links, flows, display_graph=args.graph,
                      graph_filename=args.output)
    network.run()
