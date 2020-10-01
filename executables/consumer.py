#!./venv/bin/python
import logging
import os
import sys
import time
from argparse import ArgumentParser
from itertools import cycle
from pprint import pprint
from urllib import unquote

import numpy as np
import pandas as pd
from numpy import random
from pyndn import Interest, Name, Face
from pyndn.threadsafe_face import ThreadsafeFace

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 600)

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format="%(levelname)s [%(name)s] %(message)s"
)

np.random.seed = 123

import logging

Interest.setDefaultCanBePrefix(False)

if __name__ == '__main__':
    log = logging.getLogger("app:main")

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-p", "--prefixes", type=str, nargs="*", help="Prefix for all requests")
    arg_parser.add_argument("-i", "--interval", type=float, default=1.0, help="Time between requests")
    arg_parser.add_argument("-r", "--range", type=int, nargs=2, help="Range of requests")
    arg_parser.add_argument("-z", "--zipf", type=float, help="Zipf alpha parameter")
    arg_parser.add_argument("-l", "--length", type=int, help="Max name length")
    arg_parser.add_argument("-lt", "--log-times", type=str, help="Log requests RTT")
    arg_parser.add_argument("--dry", "--dry-run", action="store_true", help="Only print requests")
    arg_parser.add_argument("--info", action="store_true", help="Only print dataset info")
    arg_parser.add_argument("requests", type=str, help="File containing the requests")

    args = arg_parser.parse_args()

    face = Face()

    requests = pd.read_csv(args.requests, keep_default_na=False)["destination"].unique()

    if args.prefixes is not None:
        pref = args.prefixes
        l_pref = len(args.prefixes)
        requests = ["/%s/%s" % (pref.strip("/"), r.lstrip("/")) for pref, r in zip(cycle(args.prefixes), requests)]

    if args.range is not None:
        requests = requests[args.range[0]:args.range[1]]

    if args.info:
        print("Content domain: %d" % len(requests))
        pprint(requests[:5])
        print("...")
        pprint(requests[-6:-1])
        exit(0)

    weights = None
    if args.zipf:
        n = len(requests)
        x = np.arange(1, n + 1)
        a = args.zipf
        weights = x ** (-a)
        weights /= weights.sum()


    def send_request(name):
        if args.length is not None:
            name = name.getPrefix(args.length)

        if args.dry:
            log.info("Dry: %s" % unquote(name.toUri()))
            return

        interest = Interest() \
            .setMustBeFresh(False) \
            .setCanBePrefix(True) \
            .setInterestLifetimeMilliseconds(5000.0) \
            .setName(name)

        req_time = time.time()

        face.expressInterest(
            interest,
            lambda i, d: log.info(
                "%.5f [%.5f] Data: %s -> %s" % (
                    time.time(), time.time() - req_time, unquote(i.getName().toUri()), d.content.toRawStr())),
            lambda i: log.warning("Timeout: %s" % unquote(i.getName().toUri())),
            lambda i, n: log.warning("NACK: %s" % unquote(i.getName().toUri())))


    def iter_requests():
        while True:
            content_name = Name(str(random.choice(requests, replace=True, p=weights)))
            send_request(content_name)
            face.processEvents()
            time.sleep(args.interval)


    # Run client and check for exceptions
    try:
        iter_requests()
    except (KeyboardInterrupt, SystemExit):
        face.shutdown()
        sys.exit("Ok, bye!")

    print("Completed!")
