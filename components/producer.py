from minindn.apps.application import Application
from mininet.log import info, debug

from components import DOMAINS_PATH, EXECUTABLES_PATH, BASE_PATH


class ProducerService(Application):
    def __init__(self, node, **appParams):
        super(ProducerService, self).__init__(node)

        try:
            node_args = appParams.pop("nodes_args")[self.node.name]
            info("%s => %s\n" % (self.node.name, node_args))
            try:
                prefix = "-p %s " % node_args["prefix"]
            except KeyError:
                prefix = ""
            try:
                domain = "-d %s/%s " % (DOMAINS_PATH, node_args["domain"])
            except KeyError:
                domain = ""
            try:
                n_producers = "-n %d " % node_args["n_producers"]
            except KeyError:
                n_producers = ""
            try:
                i_producer = "-i %d " % node_args["i_producer"]
            except KeyError:
                i_producer = ""
            try:
                freshness = "-f %f " % node_args["freshness"]
            except KeyError:
                freshness = ""
            node_args = prefix + domain + n_producers + i_producer + freshness
        except KeyError:
            node_args = ""

        self.logFile = 'producer.log'
        self.cmd = \
            BASE_PATH + "/venv/bin/python " + \
            EXECUTABLES_PATH + "/producer.py " + \
            node_args

    def start(self, command=None, logfile=None, envDict=None):
        if command is None:
            command = self.cmd
        if logfile is None:
            logfile = self.logFile
        if envDict is None:
            envDict = {}

        debug("%s executing %s\n" % (self.node.name, command))
        super(ProducerService, self).start(command, logfile=logfile, envDict=envDict)
