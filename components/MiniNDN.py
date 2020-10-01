from argparse import ArgumentParser
from os.path import abspath

import yaml
from minindn.helpers.nfdc import Nfdc
from minindn.minindn import Minindn
from mininet.topo import Topo
from typing import List


class MyMinindn(Minindn):
    def __init__(self, parser, **mininetParams):

        parser = MyMinindn.parseArgs(parser)

        args, _ = parser.parse_known_args()

        self.faceProtocol = args.faceProtocol
        self.routing = args.routingType
        self.cs_strategy = args.cs_strategy
        self.domain_file = abspath(args.domain_file)
        self.domain_size = args.domain_size
        self.topology_file = args.topology

        topology, self.name_mapping, self.environments, self.groups = \
            MyMinindn.process_custom_topology(self.topology_file)

        super(MyMinindn, self).__init__(parser=parser, topo=topology, **mininetParams)

    @staticmethod
    def parseArgs(parent):
        parser = ArgumentParser(parents=[parent], conflict_handler='resolve')

        parser.add_argument(
            '--face-protocol', dest='faceProtocol',
            default=Nfdc.PROTOCOL_UDP,
            choices=[Nfdc.PROTOCOL_UDP, Nfdc.PROTOCOL_TCP, Nfdc.PROTOCOL_ETHER])
        parser.add_argument(
            '--routing', dest='routingType', default='link-state',
            choices=['link-state', 'hr', 'dry'],
            help="Choose routing type, dry = link-state is used but hr is calculated for comparison.")
        parser.add_argument("--domain_size", type=int, help="Maximum size of the domain")
        parser.add_argument(
            "-s", "--cs_strategy", help="Strategy to use during the simulation",
            choices=["lru", "lfu", "priority_fifo", "popularity"], default="lru")
        parser.add_argument("domain_file", help="Path to domain file", type=str)
        parser.add_argument("topology", help="Topology YAML file")

        return parser

    @staticmethod
    def process_custom_topology(topology_file):
        topo = Topo()
        with open(topology_file) as f:
            topo_data = yaml.full_load(f)

        name_mapping = {}
        environments = {}
        groups = {}
        for group in topo_data.keys():
            if group == "connections":
                continue
            groups[group] = []
            if topo_data[group] is not None:
                for node, env in topo_data[group].items():
                    node_name = "%s_%s" % (group[:2].upper(), node)
                    name_mapping[node] = node_name
                    environments[node_name] = env
                    groups[group].append(node_name)
                    topo.addHost(node_name)

        for node_name in name_mapping.values():
            environments[node_name]["NODE_PREFIX"] = "/ndn/%s-site/%s" % (node_name, node_name)

        for couple in topo_data["connections"]:
            for node_A, node_B in couple.items():
                if not isinstance(node_B, List) and node_A != node_B:
                    topo.addLink(name_mapping[node_A], name_mapping[node_B], delay='10ms')

        return topo, name_mapping, environments, groups
