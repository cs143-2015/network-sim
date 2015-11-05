from components import Network, Link, Host

if __name__ == '__main__':
    H1 = Host("H1")
    H2 = Host("H2")
    L1 = Link("L1", 10.0,10,64, H1, H2)
    network = Network([H1, H2], [], [L1], [])
    network.run()
