#!/usr/bin/env python2

from argparse import ArgumentParser

from utilities.topology import parse_topology_data, plot_topology

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("topology", help="Topology definition file")

    args = parser.parse_args()

    topology_data = parse_topology_data(args.topology)
    plot_topology(topology_data)
