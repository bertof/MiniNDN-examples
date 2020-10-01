from pprint import pformat

import minindn
from minindn.apps.application import Application
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from mininet.log import info

from components.MiniNDN import MyMinindn


class CustomNFD(Nfd):

    def __init__(self, node, environments=None, logLevel='NONE',
                 csSize=65536, csPolicy="lru", csUnsolicitedPolicy="admit-all"):
        super(CustomNFD, self).__init__(node, logLevel, csSize, csPolicy, csUnsolicitedPolicy)
        if environments is None:
            environments = {}
        environments[self.node.name]["DUMP_ENABLED"] = "%s/cs_dump.csv" % self.logDir
        self.environments = environments

    def start(self):
        info(self.node.name + " = " + pformat(self.environments[self.node.name]) + "\n")
        Application.start(self, 'nfd --config %s' % self.confFile,
                          logfile=self.logFile, envDict=self.environments[self.node.name])
        MyMinindn.sleep(minindn.helpers.nfdc.SLEEP_TIME)
