from argparse import ArgumentParser

import yaml
from minindn.helpers.nfdc import Nfdc
from minindn.minindn import Minindn
from mininet.topo import Topo


class MyMinindn(Minindn):
    def __init__(self, parser, **mininetParams):

        parser = MyMinindn.parse_args(parser)

        args, _ = parser.parse_known_args()

        self.faceProtocol = args.faceProtocol
        self.routing = args.routingType
        self.cs_strategy = args.cs_strategy
        self.domain_file = args.domain
        self.domain_size = args.domain_size
        self.topology_file = args.topology

        topology, self.name_mapping, self.environments, self.groups = \
            MyMinindn.process_custom_topology(self.topology_file)

        super(MyMinindn, self).__init__(parser=parser, topo=topology, **mininetParams)

    @staticmethod
    def parse_args(parent):
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
            "cs_strategy", help="Strategy to use during the simulation",
            choices=["lru", "lfu", "priority_fifo", "popularity"])
        parser.add_argument("domain", help="Path to domain file", )
        parser.add_argument("topology", help="Topology YAML file")

        return parser

    @staticmethod
    def process_custom_topology(topology_file):
        topology = Topo()
        with open(topology_file) as f:
            topology_data = yaml.full_load(f)

        name_mapping = {}
        environments = {}
        groups = {}
        for group in ["attackers", "producers", "consumers", "aggregators", "routers"]:
            groups[group] = []
            if topology_data[group] is not None:
                for node, env in topology_data[group].items():
                    node_name = "%s_%s" % (group[:2].upper(), node)
                    name_mapping[node] = node_name
                    environments[node_name] = env
                    groups[group].append(node_name)
                    topology.addHost(node_name)

        return topology, name_mapping, environments, groups
