from components import Network, Link, Host, Router

if __name__ == '__main__':
    print "---------------------------- Test Case 0 ---------------------------"
    H1 = Host("H1")
    H2 = Host("H2")
    L1 = Link("L1", 10.0, 10, 64, H1, H2)
    network = Network([H1, H2], [], [L1], [])
    # network.run()

    print "---------------------------- Test Case 1 ---------------------------"

    # Creates the following graph
    #                    R_b
    #                  /     \
    # H1 --- L5 --- R_a       R_c -- L5 -- H2
    #                  \     /
    #                    R_d
    # The links L1-L4 connect Routers a-d in a clockwise order starting from a

    # # Same hosts as before
    # R_a = Router("a")
    # R_b = Router("b")
    # R_c = Router("c")
    # R_d = Router("d")
    # L1 = Link("L1", 1.0, 10, 64, R_a, R_b)
    # L2 = Link("L2", 2.0, 10, 64, R_b, R_c)
    # L3 = Link("L3", 3.0, 10, 64, R_c, R_d)
    # L4 = Link("L4", 4.0, 10, 64, R_d, R_a)
    # L5 = Link("L5", 1.0, 10, 64, H1, R_a)
    # L6 = Link("L6", 1.0, 10, 64, H2, R_c)
    # network = Network([H1, H2],
    #                   [R_a, R_b, R_c, R_d],
    #                   [L1, L2, L3, L4, L5, L6],
    #                   [])
    # network.run()

    # No hosts
    R_1 = Router("n1")
    R_2 = Router("n2")
    R_3 = Router("n3")
    R_4 = Router("n4")
    R_5 = Router("n5")
    L12 = Link("L1-2", 1.0, 10, 64, R_1, R_2)
    L23 = Link("L2-3", 2.0, 10, 64, R_2, R_3)
    L35 = Link("L3-5", 5.0, 10, 64, R_3, R_5)
    L25 = Link("L2-5", 4.0, 10, 64, R_2, R_5)
    L45 = Link("L4-5", 6.0, 10, 64, R_4, R_5)
    L14 = Link("L1-4", 3.0, 10, 64, R_1, R_4)
    network = Network([H1, H2],
                      [R_1, R_2, R_3, R_4, R_5],
                      [L12, L23, L25, L35, L45, L14],
                      [])
    network.run()

