import xml.etree.ElementTree as et

from components import Host, Router, Link


class Parser:
    def __init__(self, filename):
        """
        Initialize XML parser

        :param filename: Path to XML filename
        :type filename: str
        :return: Parser
        :rtype: Parser
        """
        self.filename = filename

    def parse(self):
        """
        Parses the XML file

        :return: Hosts, routers, links and flows
        :rtype: (list[Host], list[Router], list[Link])
        """
        hosts = {}
        routers = {}
        links = []

        tree = et.parse(self.filename)
        root = tree.getroot()

        for host in root.iter('host'):
            host_id = host.attrib['id']
            new_host = Host(host_id)
            hosts[host_id] = new_host

        for router in root.iter('router'):
            router_id = router.attrib['id']
            dynamic_routing = self.bool_parse(router.attrib['dynamic_routing'])
            new_router = Router(router_id, dynamic_routing)
            routers[router_id] = new_router

        for link in root.iter('link'):
            rate = float(link.attrib['rate'])
            delay = float(link.attrib['delay'])
            buffer_size = float(link.attrib['buffer-size'])

            node1_id = link.attrib['node1']
            node2_id = link.attrib['node2']

            if node1_id in hosts:
                node1 = hosts[node1_id]
            else:
                node1 = routers[node1_id]

            if node2_id in hosts:
                node2 = hosts[node2_id]
            else:
                node2 = routers[node2_id]

            new_link = Link(link.attrib['id'], rate, delay,
                            buffer_size, node1, node2)
            links.append(new_link)

        for flow in root.iter('flow'):
            start = float(flow.attrib['start'])
            amount = float(flow.attrib['amount'])
            src = hosts[flow.attrib['src']]
            dest = hosts[flow.attrib['dest']]
            src.set_flow(flow.attrib['id'], dest, amount, start)

        return hosts.values(), routers.values(), links

    @staticmethod
    def bool_parse(string):
        assert string == str(True) or string == str(False), "String is not bool"
        return True if string == str(True) else False
