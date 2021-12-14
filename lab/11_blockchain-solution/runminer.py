from argparse import ArgumentParser
from miner import Miner
import sys
import signal

miner = None


def signal_handler(sig, frame):
    global miner
    print(f'\n\nStopping Miner {miner.name}')
    miner.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

parser = ArgumentParser(description='Deploy a local miner node')
parser.add_argument('-k', '--host', action='store',
                    default='localhost', help='hostname to bind to')
parser.add_argument('-p', '--port', action='store', type=int,
                    required=True, help='port to bind to')

if __name__ == '__main__':
    args = parser.parse_args()
    miner = Miner(host=args.host, port=args.port)
    miner.start()
