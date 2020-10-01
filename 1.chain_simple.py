#!/usr/bin/env python2

import argparse
from os.path import abspath, dirname
from pprint import pformat

import minindn.helpers.nfdc
from minindn.apps.app_manager import AppManager
from minindn.apps.application import Application
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.util import MiniNDNCLI
from mininet.log import setLogLevel, info, debug

from components.MiniNDN import MyMinindn
from components.NFD import CustomNFD
from components.consumer import setup_consumers, ConsumerService
from components.producer import setup_producers

minindn.helpers.nfdc.SLEEP_TIME = 0.5

SHELL = False
SIMULATIONS_PATH = abspath(dirname(__file__))
EXECUTABLES_PATH = abspath(dirname(__file__) + "/executables")
DOMAINS_PATH = abspath(dirname(__file__) + "/domains")

CACHE_SIZE = 300
GAMMA = 2.5
CONSUMER_INTEREST_INTERVAL = 0.5  # Seconds
ATTACKER_INTEREST_INTERVAL = CONSUMER_INTEREST_INTERVAL / GAMMA  # Seconds

CONSUMER_DOMAIN_RANGE = 0, 5000
ATTACKER_DOMAIN_RANGE = CONSUMER_DOMAIN_RANGE[1], CONSUMER_DOMAIN_RANGE[1] + (CACHE_SIZE / 2)
ZIPF_DISTRIBUTION = 0.95

if __name__ == '__main__':
    setLogLevel('info')

    MyMinindn.cleanUp()
    MyMinindn.verifyDependencies()

    # # Disable security
    # MyMinindn.ndnSecurityDisabled = True

    parser = argparse.ArgumentParser()
    network = MyMinindn(parser=parser)

    try:
        network.start()

        # NFD
        info("Starting NFD on nodes\n")
        nfds = AppManager(network, network.net.hosts, CustomNFD,
                          environments=network.environments,
                          csPolicy=network.args.cs_strategy,
                          csSize=CACHE_SIZE,
                          csUnsolicitedPolicy="admit-all")

        # NLSR
        info('Starting NLSR on nodes\n')
        nlsrs = AppManager(network, network.net.hosts, Nlsr)

        # Producers
        producers = [n for n in network.net.hosts if n.name in network.groups["producers"]]
        info("Starting NDN producers on %s\n" % network.groups["producers"])
        producers_s = setup_producers(network, producers)

        # Consumers
        consumers = [n for n in network.net.hosts if n.name in network.groups["consumers"]]
        info("Starting NDN consumers on %s\n" % network.groups["consumers"])
        consumers_s = AppManager(
            network, consumers, ConsumerService,
            target=network.domain_file, zipf=ZIPF_DISTRIBUTION,
            interval=CONSUMER_INTEREST_INTERVAL, range=range,
            prefixes=' '.join(["/ndn/%s-site/%s" % (p, p) for p in sorted(network.groups["producers"])]))

        MiniNDNCLI(network.net)
    except KeyboardInterrupt:
        network.stop()

    network.cleanUp()

    info("END\n")
