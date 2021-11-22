#!/usr/bin/env python
from argparse import ArgumentParser

import server

# def generate_url(string):
#     host, port, name = string.split(':')
#     return f'http://{host}:{port}/', name


if __name__ == '__main__':
    parser = ArgumentParser(description='PiplinedDHT -- A simple distributed hash table')
    parser.add_argument('-n', '--name', action='store', required=True, help='node prefix name')
    parser.add_argument('-k', '--host', action='store', default='localhost', help='hostname to bind to')
    parser.add_argument('-p', '--port', action='store', type=int, required=True, help='starting port to bind to')
    parser.add_argument('-S', '--succ', action='store', help='predecessor')
    parser.add_argument('-P', '--pred', action='store', help='successor')

    args = parser.parse_args()
    server.start_node(host=args.host, port=args.port, name=args.name)
