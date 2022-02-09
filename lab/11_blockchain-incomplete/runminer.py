#!/usr/bin/env python

import signal
import sys
from argparse import ArgumentParser

from miner import Miner

miner = None

def signal_handler(signal, frame):
    global miner
    print(f'\n\nYou pressed Ctrl+C! Stopping {miner.name}')
    miner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

parser: ArgumentParser = ArgumentParser(description='Miner -- deploy a local miner.')
parser.add_argument('-k', '--host', action='store', default='localhost', help='hostname to bind to')
parser.add_argument('-p', '--port', action='store', type=int, required=True, help='port to bind to')

if __name__ == '__main__':
    args: {} = parser.parse_args()
    miner: 'Miner' or None = Miner(args.host, args.port)
    miner.start()
