from components import Network, Link, Host, Router, Flow
from utils import Logger, LoggerLevel

if __name__ == '__main__':
    H1 = Host("H1")
    H2 = Host("H2")
    L1 = Link("L1", 10.0, 10, 16, H1, H2)
    F1 = Flow("F1", H1, H2, 512/1024., 0)
    F2 = Flow("F2", H2, H1, 512/1024., 0)
    network = Network([H1, H2], [], [L1], [F1, F2])
    network.run()
