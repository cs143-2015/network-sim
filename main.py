from components import Network, Link, Host, Router, Flow
from utils import Logger, LoggerLevel
import sys
import xml.etree.ElementTree as ET

def parse_file(file_name):
    hosts = {}
    routers = {}
    links = []
    flows = []

    tree = ET.parse(file_name)
    root = tree.getroot()

    for host in root.iter('host'):
        host_id = host.attrib['id']
        new_host = Host(host_id)
        hosts[host_id] = new_host

    for router in root.iter('router'):
        router_id = router.attrib['id']
        new_router = Router(router_id)
        routers[router_id] = new_router

    for link in root.iter('link'):
        rate = float(link.attrib['rate'])
        delay = int(link.attrib['delay'])
        buffer_size = int(link.attrib['buffer-size'])

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


        new_link = Link(link.attrib['id'], rate, delay, buffer_size, node1, node2)
        links.append(new_link)

    for flow in root.iter('flow'):
        start = float(flow.attrib['start'])
        amount = float(flow.attrib['amount'])
        new_flow = Flow(flow.attrib['id'], hosts[flow.attrib['src']], hosts[flow.attrib['dest']], amount, start)
        flows.append(new_flow)

    return hosts.values(), routers.values(), links, flows

if __name__ == '__main__':
    hosts, routers, links, flows = parse_file(sys.argv[1])

    network = Network(hosts, routers, links, flows)
    network.run()



