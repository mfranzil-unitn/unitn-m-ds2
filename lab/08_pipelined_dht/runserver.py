#!/usr/bin/env python
import threading
from argparse import ArgumentParser

import server


def generate_url(string):
    host, port, name = string.split(':')
    return f'http://{host}:{port}/', name


if __name__ == '__main__':
    parser = ArgumentParser(description='PiplinedDHT -- A simple distributed hash table')
    parser.add_argument('-n', '--name', action='store', required=True, help='node prefix name')
    parser.add_argument('-k', '--host', action='store', default='localhost', help='hostname to bind to')
    parser.add_argument('-p', '--port', action='store', type=int, required=True, help='starting port to bind to')
    parser.add_argument('-S', '--succ', action='store', help='predecessor')
    parser.add_argument('-P', '--pred', action='store', help='successor')

    args = parser.parse_args()

   # n0t = threading.Thread(target=
   #                        server.start_node(host=args.host, port=args.port, name=args.name + "0"))
    #node_0 = f'{str(args.host)}:{str(args.port)}:{str(args.name)}0'
    server.start_node(host=args.host, port=args.port + 1, name=args.name + "1")
    node_1 = f'{str(args.host)}:{str(args.port + 1)}:{str(args.name)}1'

    #•requests.put(generate_url(node_0)[0] + 'succ', data={'succ': node_1})
    #çrequests.put(generate_url(node_1)[0] + 'pred', data={'pred': node_0})
