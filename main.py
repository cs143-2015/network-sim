from components import Network, Link, Host, Router

if __name__ == '__main__':
    print "---------------------------- Test Case 0 ---------------------------"
    H1 = Host("H1")
    H2 = Host("H2")
    L1 = Link("L1", 10.0, 10, 64, H1, H2)
    network = Network([H1, H2], [], [L1], [])
    # network.run()

    print "---------------------------- Test Case 1 ---------------------------"
