#!/usr/bin/env python

from argparse import ArgumentParser

from dht.server import start_app

if __name__ == '__main__':
    parser = ArgumentParser(
        description='PiplineDHT -- A simple distributed hash table')
    parser.add_argument('-n', '--name', action='store', required=True,
                        help='name of node')
    parser.add_argument('-k', '--host', action='store', default='localhost',
                        help='hostname to bind to')
    parser.add_argument('-p', '--port', action='store', type=int,
                        required=True, help='port to bind to')

    parser.add_argument('-v', '--pred', action='store',
                        required=False, help='initial predecessor')
    parser.add_argument('-s', '--succ', action='store',
                        required=False, help='initial successor')

    args = parser.parse_args()

    start_app(host=args.host, port=args.port, name=args.name, pred=args.pred, succ=args.succ)
