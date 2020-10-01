#!./venv/bin/python
import logging
import os
import string
import sys
from argparse import ArgumentParser
from random import choice
from urllib import unquote

import pandas as pd
from pyndn import Name, Interest, Data, MetaInfo, NetworkNack
from pyndn.security import KeyChain
from pyndn.threadsafe_face import ThreadsafeFace

try:
    import asyncio
except ImportError:
    import trollius as asyncio

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format="%(levelname)s [%(name)s] %(message)s"
)

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 600)

Interest.setDefaultCanBePrefix(True)

ALPHABET = string.ascii_lowercase + string.digits


def rand_string(length):
    return ''.join([choice(ALPHABET) for _ in range(length)])


SERVER_RESTART_TIMEOUT = 5000.0  # ms
FRESHNESS_PERIOD = 10000.0  # ms
if __name__ == '__main__':
    log = logging.getLogger("app:main")

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-p", "--prefix", type=str, default="", help="Prefix for all requests")
    arg_parser.add_argument("-f", "--freshness", type=float, default=FRESHNESS_PERIOD,
                            help="Data packet freshness in ms")
    arg_parser.add_argument("-d", "--domain", type=str, help="Path to domain file")
    arg_parser.add_argument("-n", "--n_producers", type=int, help="Number of producers")
    arg_parser.add_argument("-i", "--i_producer", type=int, help="Index of producer")

    args = arg_parser.parse_args()

    log.info(args)

    domain = None
    if args.domain is not None:
        domain = ["/%s/%s" % (args.prefix.strip("/"), d.lstrip("/")) for d in
                  pd.read_csv(args.domain)["destination"].unique()]
        if args.n_producers is not None and args.i_producer is not None:
            domain = [n for i, n in enumerate(domain) if (i % args.n_producers) == args.i_producer]
        domain = set(domain)
        log.info("Domain size: %d" % len(domain))

    loop = asyncio.get_event_loop()
    face = ThreadsafeFace(loop)

    keyChain = KeyChain()
    face.setCommandSigningInfo(keyChain, keyChain.getDefaultCertificateName())


    def on_register_success(prefix, *k):
        log.info("%s listening on %s" % (log.name, prefix))
        pass


    def on_register_failed(prefix, *k):
        log.error("Failed to register prefix %s" % prefix)
        loop.call_later(
            SERVER_RESTART_TIMEOUT / 1000.0,
            face.registerPrefix,
            prefix,
            on_interest,
            on_register_failed,
            on_register_success)


    def on_interest(prefix, interest, *k):
        should_respond = True

        if domain is not None:
            should_respond = False
            target = unquote(str(interest.getName().toUri()))
            if target in domain:
                should_respond = True

        if should_respond:
            content = rand_string(10)
            data = Data(interest.getName())
            meta = MetaInfo()
            meta.setFreshnessPeriod(args.freshness)
            data.setMetaInfo(meta)
            data.setContent(content)
            keyChain.sign(data, keyChain.getDefaultCertificateName())
            face.putData(data)
            log.debug("Answering to %s" % interest.getName())
        else:
            nack = NetworkNack()
            nack.setReason(NetworkNack.Reason.NO_ROUTE)
            face.putNack(interest=interest, networkNack=nack)


    face.registerPrefix(
        Name(args.prefix), on_interest,
        on_register_failed, on_register_success)

    # Run client and check for exceptions
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit("Ok, bye!")

    print("Completed!")
