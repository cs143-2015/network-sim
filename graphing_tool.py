import argparse
from utils.grapher import Grapher


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        help="The filenames of the csv file to plot",
                        nargs="*",
                        type=str)
    parser.add_argument("bucket_size",
                        help="Size of the bucket to use for graph smoothing",
                        nargs="*",
                        type=int,
                        default=None)
    return parser

if __name__ == '__main__':
    # Parse command line arguments
    args = get_argument_parser().parse_args()
    # Plot the files
    grapher = Grapher()
    assert args.bucket_size is None or \
        len(args.filenames) == len(args.bucket_size), \
        "Need a bucket width for every graph"
    for i, filename in enumerate(args.filenames):
        bucket_size = args.bucket_size[i] if args.bucket_size else None
        grapher.plot_csv(filename, bucket_size)
    # Show the graphs
    grapher.show()
