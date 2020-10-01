from logging import debug

from minindn.apps.app_manager import AppManager
from minindn.apps.application import Application

from components import EXECUTABLES_PATH, BASE_PATH


class ConsumerService(Application):
    def __init__(self, node, **appParams):
        super(ConsumerService, self).__init__(node)

        target = appParams.pop("target")

        try:
            prefixes = "-p %s " % appParams.pop("prefixes")
        except KeyError:
            prefixes = ""
        try:
            interval = "-i %f " % appParams.pop("interval")
        except KeyError:
            interval = ""
        try:
            low, up = appParams.pop("range")
            domain_range = "-r %d %d " % (low, up)
        except KeyError:
            domain_range = ""
        try:
            zipf = "-z %s " % appParams.pop("zipf")
        except KeyError:
            zipf = ""
        try:
            length = "-l %d " % appParams.pop("length")
        except KeyError:
            length = ""
        try:
            delay = "sleep %d && " % appParams.pop("delay")
        except KeyError:
            delay = ""
        try:
            if appParams.pop("dry"):
                dry = "--dry "
            else:
                dry = ""
        except KeyError:
            dry = ""
        try:
            self.logFile = appParams.pop("log")
        except KeyError:
            self.logFile = 'consumer.log'

        self.prefix = prefixes
        self.cmd = \
            delay + \
            BASE_PATH + "/venv/bin/python " + \
            EXECUTABLES_PATH + "/consumer.py " + \
            prefixes + interval + domain_range + zipf + length + dry + target

    def start(self, command=None, logfile=None, envDict=None):
        if command is None:
            command = self.cmd
        if logfile is None:
            logfile = self.logFile
        if envDict is None:
            envDict = {}

        debug("%s executing %s\n" % (self.node.name, command))
        super(ConsumerService, self).start(command, logfile=logfile, envDict=envDict)


def setup_consumers(network, consumers, zipf=None, interval=None, range=None, target=None):
    return AppManager(
        network, consumers, ConsumerService,
        target=target, zipf=zipf,
        interval=interval, range=range,
        prefixes=' '.join(["/ndn/%s-site/%s" % (p, p) for p in sorted(network.groups["producers"])]))
