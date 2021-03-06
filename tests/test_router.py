from mock import Mock
import unittest

from components import Link, Host, Network
from components.router import Router, LinkCostTuple


class RoutingTests(unittest.TestCase):
    def test_static_routing_table1(self):
        """
        Creates the following graph
                             r_b
                           /    \
        h1 --- l5(1) --- r_a     r_c -- l6(1) -- h2
                           \    /
                            r_d
        The links l1-l4 connect Routers a-d in a clockwise order starting at r_a
        with cost 1-4 for links l1-l4 respectively
        """
        h1 = Host("h1")
        h2 = Host("h2")

        r_a = Router("a", False)
        r_b = Router("b", False)
        r_c = Router("c", False)
        r_d = Router("d", False)

        l1 = Link("L1", 1.0, 10, 64, r_a, r_b)
        l2 = Link("L2", 2.0, 10, 64, r_b, r_c)
        l3 = Link("L3", 3.0, 10, 64, r_c, r_d)
        l4 = Link("L4", 4.0, 10, 64, r_d, r_a)
        l5 = Link("L5", 1.0, 10, 64, h1, r_a)
        l6 = Link("L6", 1.0, 10, 64, h2, r_c)

        routers = [r_a, r_b, r_c, r_d]
        network = Network([h1, h2], routers, [l1, l2, l3, l4, l5, l6],
                          display_graph=False)

        # Create routing tables
        map(lambda x: x.create_routing_table(dynamic=False), routers)
        # Start the network
        network._run()

        # Expected routing tables
        rt_a = {"a": LinkCostTuple(None, 0),
                "b": LinkCostTuple(l1, 1),
                "c": LinkCostTuple(l1, 3),
                "d": LinkCostTuple(l4, 4),
                "h1": LinkCostTuple(l5, 1),
                "h2": LinkCostTuple(l1, 4)}
        # Two possible correct routing tables
        rt_b_1 = {"a": LinkCostTuple(l1, 1),
                  "b": LinkCostTuple(None, 0),
                  "c": LinkCostTuple(l2, 2),
                  "d": LinkCostTuple(l1, 5),
                  "h1": LinkCostTuple(l1, 2),
                  "h2": LinkCostTuple(l2, 3)}
        rt_b_2 = {"a": LinkCostTuple(l1, 1),
                  "b": LinkCostTuple(None, 0),
                  "c": LinkCostTuple(l2, 2),
                  "d": LinkCostTuple(l2, 5),
                  "h1": LinkCostTuple(l1, 2),
                  "h2": LinkCostTuple(l2, 3)}
        rt_c = {"a": LinkCostTuple(l2, 3),
                "b": LinkCostTuple(l2, 2),
                "c": LinkCostTuple(None, 0),
                "d": LinkCostTuple(l3, 3),
                "h1": LinkCostTuple(l2, 4),
                "h2": LinkCostTuple(l6, 1)}
        # Two possible correct routing tables
        rt_d_1 = {"a": LinkCostTuple(l4, 4),
                  "b": LinkCostTuple(l3, 5),
                  "c": LinkCostTuple(l3, 3),
                  "d": LinkCostTuple(None, 0),
                  "h1": LinkCostTuple(l4, 5),
                  "h2": LinkCostTuple(l3, 4)}
        rt_d_2 = {"a": LinkCostTuple(l4, 4),
                  "b": LinkCostTuple(l4, 5),
                  "c": LinkCostTuple(l3, 3),
                  "d": LinkCostTuple(None, 0),
                  "h1": LinkCostTuple(l4, 5),
                  "h2": LinkCostTuple(l3, 4)}
        # Failure messages
        m1 = "%s routing table is wrong.\nExpected:\n%s\nActual:\n%s"
        m2 = "%s routing table is wrong.\nExpected:\n%s\nOR\n%s\nActual:\n%s"
        self.assertEqual(rt_a, r_a.routingTable,
                         m1 % (r_a, rt_a, r_a.routingTable))
        self.assertTrue(rt_b_1 == r_b.routingTable or
                        rt_b_2 == r_b.routingTable,
                        m2 % (r_b, rt_b_1, rt_b_2, r_b.routingTable))
        self.assertEqual(rt_c, r_c.routingTable,
                         m1 % (r_c, rt_c, r_c.routingTable))
        self.assertTrue(rt_d_1 == r_d.routingTable or
                        rt_d_2 == r_d.routingTable,
                        m2 % (r_d, rt_d_1, rt_d_2, r_d.routingTable))

    def test_static_routing_table2(self):
        # No hosts
        r_1 = Router("n1", False)
        r_2 = Router("n2", False)
        r_3 = Router("n3", False)
        r_4 = Router("n4", False)
        r_5 = Router("n5", False)

        l12 = Link("L1-2", 1.0, 10, 64, r_1, r_2)
        l23 = Link("L2-3", 2.0, 10, 64, r_2, r_3)
        l35 = Link("L3-5", 5.0, 10, 64, r_3, r_5)
        l25 = Link("L2-5", 4.0, 10, 64, r_2, r_5)
        l45 = Link("L4-5", 6.0, 10, 64, r_4, r_5)
        l14 = Link("L1-4", 3.0, 10, 64, r_1, r_4)

        routers = [r_1, r_2, r_3, r_4, r_5]
        network = Network([], routers, [l12, l23, l25, l35, l45, l14],
                          display_graph=False)

        # Create routing tables
        map(lambda x: x.create_routing_table(dynamic=False), routers)
        # Start the network
        network._run()

        # Expected routing tables
        rt_1 = {"n1": LinkCostTuple(None, 0),
                "n2": LinkCostTuple(l12, 1),
                "n3": LinkCostTuple(l12, 3),
                "n4": LinkCostTuple(l14, 3),
                "n5": LinkCostTuple(l12, 5)}
        rt_2 = {"n1": LinkCostTuple(l12, 1),
                "n2": LinkCostTuple(None, 0),
                "n3": LinkCostTuple(l23, 2),
                "n4": LinkCostTuple(l12, 4),
                "n5": LinkCostTuple(l25, 4)}
        rt_3 = {"n1": LinkCostTuple(l23, 3),
                "n2": LinkCostTuple(l23, 2),
                "n3": LinkCostTuple(None, 0),
                "n4": LinkCostTuple(l23, 6),
                "n5": LinkCostTuple(l35, 5)}
        rt_4 = {"n1": LinkCostTuple(l14, 3),
                "n2": LinkCostTuple(l14, 4),
                "n3": LinkCostTuple(l14, 6),
                "n4": LinkCostTuple(None, 0),
                "n5": LinkCostTuple(l45, 6)}
        rt_5 = {"n1": LinkCostTuple(l25, 5),
                "n2": LinkCostTuple(l25, 4),
                "n3": LinkCostTuple(l35, 5),
                "n4": LinkCostTuple(l45, 6),
                "n5": LinkCostTuple(None, 0)}
        # Failure message
        m = "%s routing table is wrong.\nExpected:\n%s\nActual:\n%s"
        self.assertEqual(rt_1, r_1.routingTable,
                         m % (r_1, rt_1, r_1.routingTable))
        self.assertEqual(rt_2, r_2.routingTable,
                         m % (r_2, rt_2, r_2.routingTable))
        self.assertEqual(rt_3, r_3.routingTable,
                         m % (r_3, rt_3, r_3.routingTable))
        self.assertEqual(rt_4, r_4.routingTable,
                         m % (r_4, rt_4, r_4.routingTable))
        self.assertEqual(rt_5, r_5.routingTable,
                         m % (r_5, rt_5, r_5.routingTable))

    def test_dynamic_routing_table1(self):
        """
        Creates the following graph
                             r_b
                           /    \
        h1 --- l5(1) --- r_a     r_c -- l6(1) -- h2
                           \    /
                            r_d
        The links l1-l4 connect Routers a-d in a clockwise order starting at r_a
        with cost 1-4 for links l1-l4 respectively
        """
        h1 = Host("h1")
        h2 = Host("h2")

        r_a = Router("a", False)
        r_b = Router("b", False)
        r_c = Router("c", False)
        r_d = Router("d", False)

        l1 = Link("L1", 1.0, 10, 64, r_a, r_b)
        l2 = Link("L2", 2.0, 10, 64, r_b, r_c)
        l3 = Link("L3", 3.0, 10, 64, r_c, r_d)
        l4 = Link("L4", 4.0, 10, 64, r_d, r_a)
        l5 = Link("L5", 1.0, 10, 64, h1, r_a)
        l6 = Link("L6", 1.0, 10, 64, h2, r_c)

        routers = [r_a, r_b, r_c, r_d]
        network = Network([h1, h2], routers, [l1, l2, l3, l4, l5, l6],
                          display_graph=False)
        # Don't execute subsequent updates
        Router.handle_same_dynamic_routing_table = self.execute_pass

        # Create routing tables
        map(lambda x: x.create_routing_table(dynamic=True), routers)
        # Start the network
        network._run()

        # Expected initial static routing tables
        rt_a = {"a": LinkCostTuple(None, 0),
                "b": LinkCostTuple(l1, 1),
                "c": LinkCostTuple(l1, 3),
                "d": LinkCostTuple(l4, 4),
                "h1": LinkCostTuple(l5, 1),
                "h2": LinkCostTuple(l1, 4)}
        # Two possible correct routing tables
        rt_b_1 = {"a": LinkCostTuple(l1, 1),
                  "b": LinkCostTuple(None, 0),
                  "c": LinkCostTuple(l2, 2),
                  "d": LinkCostTuple(l1, 5),
                  "h1": LinkCostTuple(l1, 2),
                  "h2": LinkCostTuple(l2, 3)}
        rt_b_2 = {"a": LinkCostTuple(l1, 1),
                  "b": LinkCostTuple(None, 0),
                  "c": LinkCostTuple(l2, 2),
                  "d": LinkCostTuple(l2, 5),
                  "h1": LinkCostTuple(l1, 2),
                  "h2": LinkCostTuple(l2, 3)}
        rt_c = {"a": LinkCostTuple(l2, 3),
                "b": LinkCostTuple(l2, 2),
                "c": LinkCostTuple(None, 0),
                "d": LinkCostTuple(l3, 3),
                "h1": LinkCostTuple(l2, 4),
                "h2": LinkCostTuple(l6, 1)}
        # Two possible correct routing tables
        rt_d_1 = {"a": LinkCostTuple(l4, 4),
                  "b": LinkCostTuple(l3, 5),
                  "c": LinkCostTuple(l3, 3),
                  "d": LinkCostTuple(None, 0),
                  "h1": LinkCostTuple(l4, 5),
                  "h2": LinkCostTuple(l3, 4)}
        rt_d_2 = {"a": LinkCostTuple(l4, 4),
                  "b": LinkCostTuple(l4, 5),
                  "c": LinkCostTuple(l3, 3),
                  "d": LinkCostTuple(None, 0),
                  "h1": LinkCostTuple(l4, 5),
                  "h2": LinkCostTuple(l3, 4)}
        # Failure messages
        m1 = "%s routing table is wrong.\nExpected:\n%s\nActual:\n%s"
        m2 = "%s routing table is wrong.\nExpected:\n%s\nOR\n%s\nActual:\n%s"
        self.assertEqual(rt_a, r_a.newDynamicRoutingTable,
                         m1 % (r_a, rt_a, r_a.newDynamicRoutingTable))
        self.assertTrue(rt_b_1 == r_b.newDynamicRoutingTable or
                        rt_b_2 == r_b.newDynamicRoutingTable,
                        m2 % (r_b, rt_b_1, rt_b_2, r_b.newDynamicRoutingTable))
        self.assertEqual(rt_c, r_c.newDynamicRoutingTable,
                         m1 % (r_c, rt_c, r_c.newDynamicRoutingTable))
        self.assertTrue(rt_d_1 == r_d.newDynamicRoutingTable or
                        rt_d_2 == r_d.newDynamicRoutingTable,
                        m2 % (r_d, rt_d_1, rt_d_2, r_d.newDynamicRoutingTable))

        # Update link dynamic costs
        l1.dynamic_cost = Mock()
        l1.dynamic_cost.return_value = 4
        l2.dynamic_cost = Mock()
        l2.dynamic_cost.return_value = 3
        l3.dynamic_cost = Mock()
        l3.dynamic_cost.return_value = 2
        l4.dynamic_cost = Mock()
        l4.dynamic_cost.return_value = 1
        l5.dynamic_cost = Mock()
        l5.dynamic_cost.return_value = 1
        l6.dynamic_cost = Mock()
        l6.dynamic_cost.return_value = 1

        # Expected initial static routing tables
        rt_a = {"a": LinkCostTuple(None, 0),
                "b": LinkCostTuple(l1, 4),
                "c": LinkCostTuple(l4, 3),
                "d": LinkCostTuple(l4, 1),
                "h1": LinkCostTuple(l5, 1),
                "h2": LinkCostTuple(l4, 4)}
        # Two possible correct routing tables
        rt_b_1 = {"a": LinkCostTuple(l1, 4),
                  "b": LinkCostTuple(None, 0),
                  "c": LinkCostTuple(l2, 3),
                  "d": LinkCostTuple(l1, 5),
                  "h1": LinkCostTuple(l1, 5),
                  "h2": LinkCostTuple(l2, 4)}
        rt_b_2 = {"a": LinkCostTuple(l1, 4),
                  "b": LinkCostTuple(None, 0),
                  "c": LinkCostTuple(l2, 3),
                  "d": LinkCostTuple(l2, 5),
                  "h1": LinkCostTuple(l1, 5),
                  "h2": LinkCostTuple(l2, 4)}
        rt_c = {"a": LinkCostTuple(l3, 3),
                "b": LinkCostTuple(l2, 3),
                "c": LinkCostTuple(None, 0),
                "d": LinkCostTuple(l3, 2),
                "h1": LinkCostTuple(l3, 4),
                "h2": LinkCostTuple(l6, 1)}
        # Two possible correct routing tables
        rt_d_1 = {"a": LinkCostTuple(l4, 1),
                  "b": LinkCostTuple(l3, 5),
                  "c": LinkCostTuple(l3, 2),
                  "d": LinkCostTuple(None, 0),
                  "h1": LinkCostTuple(l4, 2),
                  "h2": LinkCostTuple(l3, 3)}
        rt_d_2 = {"a": LinkCostTuple(l4, 1),
                  "b": LinkCostTuple(l4, 5),
                  "c": LinkCostTuple(l3, 2),
                  "d": LinkCostTuple(None, 0),
                  "h1": LinkCostTuple(l4, 2),
                  "h2": LinkCostTuple(l3, 3)}

        # Create routing tables
        map(lambda x: x.create_routing_table(dynamic=True), routers)
        # Start the network again
        network.running = False
        network._run()

        self.assertEqual(rt_a, r_a.newDynamicRoutingTable,
                         m1 % (r_a, rt_a, r_a.newDynamicRoutingTable))
        self.assertTrue(rt_b_1 == r_b.newDynamicRoutingTable or
                        rt_b_2 == r_b.newDynamicRoutingTable,
                        m2 % (r_b, rt_b_1, rt_b_2, r_b.newDynamicRoutingTable))
        self.assertEqual(rt_c, r_c.newDynamicRoutingTable,
                         m1 % (r_c, rt_c, r_c.newDynamicRoutingTable))
        self.assertTrue(rt_d_1 == r_d.newDynamicRoutingTable or
                        rt_d_2 == r_d.newDynamicRoutingTable,
                        m2 % (r_d, rt_d_1, rt_d_2, r_d.newDynamicRoutingTable))

    def execute_pass(self):
        pass
