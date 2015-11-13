from components import Network, Link, Host, Router, Flow
from utils import Logger, LoggerLevel
import sys
import xml.etree.ElementTree as ET

if __name__ == '__main__':
    
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    hostlist = {}
     
    for host in root.iter('host'):
        host_id = host.attrib['id']
        newhost = Host(host_id)
        hostlist[host_id] = newhost

    links = []
    for link in root.iter('link'):
        rate = float(link.attrib['rate'])
        delay = int(link.attrib['delay'])
        buffer_size = int(link.attrib['buffer-size'])
        newlink = Link(link.attrib['id'], rate, delay, buffer_size, hostlist[link.attrib['node1']], hostlist[link.attrib['node2']])
        links.append(newlink)

    flows = []
    for flow in root.iter('flow'):
        start = float(flow.attrib['start'])
        amount = int(flow.attrib['amount'])
        newflow = Flow(flow.attrib['id'], hostlist[flow.attrib['src']], hostlist[flow.attrib['dest']], amount, start)
        flows.append(newflow)

    network = Network(hostlist.values(), [], links, flows)
    network.run()


    