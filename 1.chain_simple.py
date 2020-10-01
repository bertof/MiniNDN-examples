#!/usr/bin/env python2

import logging
import os
from argparse import ArgumentParser

import minindn.helpers.nfdc
from minindn.apps.app_manager import AppManager
from minindn.apps.nlsr import Nlsr
from minindn.util import MiniNDNCLI

from components.MiniNDN import MyMinindn
from components.NFD import CustomNFD
from components.producer import setup_producers

minindn.helpers.nfdc.SLEEP_TIME = 0.5

CACHE_SIZE = 50
CONSUMER_DOMAIN_RANGE = 0, 5000
ATTACKER_DOMAIN_RANGE = CONSUMER_DOMAIN_RANGE[1], CONSUMER_DOMAIN_RANGE[1] + (CACHE_SIZE / 2)
ZIPF_DISTRIBUTION = 0.95

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format="%(levelname)s [%(name)s] %(message)s"
)

if __name__ == '__main__':
    MyMinindn.cleanUp()
    MyMinindn.verifyDependencies()

    parser = ArgumentParser()

    ndn = MyMinindn(parser=parser)

    try:
        logging.info("Starting NFD on nodes")
        nfds = AppManager(ndn, ndn.net.hosts, CustomNFD,
                          environments=ndn.environments,
                          csPolicy=ndn.args.cs_strategy,
                          csSize=CACHE_SIZE,
                          csUnsolicitedPolicy="admit-all")

        logging.info("Starting NLSR on nodes")
        nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

        # Producers
        producers = [n for n in ndn.net.hosts if n.name in ndn.groups["producers"]]
        logging.info("Starting NDN producers on %s" % ndn.groups["producers"])
        setup_producers(ndn, producers)

        # Star CLI
        MiniNDNCLI(ndn.net)

    except KeyboardInterrupt:
        ndn.stop()

    ndn.cleanUp()
    logging.info("END\n")
