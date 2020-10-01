from os.path import abspath

from minindn.apps.app_manager import AppManager
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
                domain = "-d %s " % node_args["domain_file"]
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


def setup_producers(network, producers):
    nodes_args = {}
    for i, node_name in enumerate(sorted(network.groups["producers"])):
        nodes_args[node_name] = {
            "domain_file": network.domain_file,
            "prefix": "/ndn/%s-site/%s" % (node_name, node_name),
            "n_producers": len(producers),
            "i_producer": i
        }

    producers_s = AppManager(network, producers, ProducerService, nodes_args=nodes_args)
    return producers_s
