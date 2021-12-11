import hashlib
from typing import AnyStr

import networkx as nx
from bitstring import BitArray
from matplotlib import pyplot as plt
from tabulate import tabulate

BITLENGTH = 140


def compute_key(string: str, bitlength: int = BITLENGTH):
    digest = hashlib.sha256(bytes(string, "utf-8")).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    return BitArray(bin=subbin).uint


def clock_dist(a: int, b: int, maxnum=2 ** BITLENGTH - 1):
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)


class NodeDHT:
    def __init__(self, name: str):
        self.name: str = name
        self.id: int = compute_key(name)
        self.succ: 'NodeDHT' = self
        self.pred: 'NodeDHT' = self
        self.storage: {} = {}
        self.ft: {} = {}

    def set_successor(self, node: 'NodeDHT'):
        self.succ = node

    def set_predecessor(self, node: 'NodeDHT'):
        self.pred = node

    def join(self, requester: 'NodeDHT') -> ('NodeDHT', 'NodeDHT'):
        if not sanity_check(self, requester):
            raise ValueError("Conflicting hash, please raise bitlength")

        target, _ = find_node(self, requester.id)

        requester.set_predecessor(target)
        requester.set_successor(target.succ)

        target.succ.set_predecessor(requester)
        target.set_successor(requester)

        if target.storage != {}:
            # Rebalancing content distribution
            for k, v in target.storage.copy().items():
                newresp, _ = find_node(self, k)
                if newresp.id == requester.id:
                    requester.store(k, target.storage[k])
                    del target.storage[k]

    def leave(self) -> bool:
        # self.pred.ht.update(self.ht)
        self.pred.set_successor(self.succ)
        self.succ.set_predecessor(self.pred)

        for i in self.storage.keys():
            value = self.storage[i]
            self.pred.store(i, value)

        return True

    def store(self, key: 'int', value: str) -> 'NodeDHT':
        target, _ = find_node(self, key)
        target.storage[key] = value
        return target

    def remove(self, key: 'int') -> str:
        target, _ = find_node(self, key)
        retval = target.storage[key]
        del target.storage[key]
        return retval

    def lookup(self, key: 'int') -> ('str', int) or (None, int):
        target, rec = find_node(self, key)
        try:
            value = target.storage[key]
            print(f"{key} -> {value} @ {target}")
            return value, rec
        except KeyError:
            print(f"{key} Ø")
            return None, rec

    def print_storage(self) -> None:
        print(f"{self}")
        print("---------------")
        for key, value in sorted(self.storage.items()):
            print(f"{key} -> {value}")
        print("---------------")
        print("\n")

    def __str__(self):
        return f"{str(self.name)}@{str(self.id)}"

    def __lt__(self, other):
        return self.id < other.id

    def __del__(self):
        pass
        # self.leave()

    def update(self) -> None:
        for x in range(BITLENGTH):
            start_from = self.ft[x] if x in self.ft else self
            finger_x, _ = find_node(start_from, (self.id + (2 ** x)) % (2 ** BITLENGTH))
            self.ft[x] = finger_x

    def find_finger(self, key: int) -> 'NodeDHT':
        current = self
        for i in range(BITLENGTH):
            if clock_dist(current.id, key) > clock_dist(self.ft[i].id, key):
                current = self.ft[i]
        return current

    def finger_lookup(self, key: int) -> (str, int):
        current = self.find_finger(key)
        next_node = current.find_finger(key)
        rec_level = 0
        while clock_dist(current.id, key) > clock_dist(next_node.id, key):
            # print("Finger: {}, succ.Finger: {}".format(current.id, next_node.id))
            current = next_node
            next_node = current.find_finger(key)
            rec_level += 1

        try:
            value = current.storage[key]
            print(f"(f) {key} -> {value} @ {current}")
            return value, rec_level
        except KeyError:
            print(f"(f) {key} Ø")
            return None, rec_level


def find_node(start_node: 'NodeDHT', key: int) -> ('NodeDHT', int):
    current = start_node
    rec_level = 0
    while clock_dist(current.id, key) > clock_dist(current.succ.id, key):
        current = current.succ
        rec_level += 1
    # print("current {}, succ {}, key {}".format(current.id, current.succ.id, key))
    return current, rec_level


def print_ring(startnode: 'NodeDHT') -> None:
    node_list = [startnode]
    next_node = startnode.succ
    while next_node != startnode:
        print(next_node)
        node_list.append(next_node)
        next_node = next_node.succ
    node_list = sorted(node_list)
    print(" -> ".join([str(x) for x in node_list]))


def print_dht(startnode: 'NodeDHT', fmt: str = 'pretty') -> 'AnyStr':
    node2content = {startnode: startnode.storage}
    next_node = startnode.succ
    while next_node != startnode:
        node2content[next_node] = next_node.storage
        next_node = next_node.succ
    tabulable = {k: sorted(list(v.items()))
                 for k, v in sorted(node2content.items())}
    return tabulate(tabulable, headers='keys', tablefmt=fmt)


def get_all_nodes(starting_node : 'NodeDHT') -> 'list[NodeDHT]':
    """Return all nodes in the DHT"""
    nodes = [starting_node]
    node = starting_node
    while node != starting_node:
        node = node.succ
        nodes.append(node)
    return nodes


def sanity_check(node_in_dht: 'NodeDHT', requester: 'NodeDHT') -> bool:
    """Sanity check for the DHT"""
    hashes = [i.id for i in get_all_nodes(node_in_dht)]
    return not requester.id in hashes

def print_dht_circle(startnode: 'NodeDHT') -> None:
    graph = nx.DiGraph()
    current = startnode
    next_node = startnode.succ

    while next_node != startnode:
        graph.add_edge(current.id, next_node.id)
        current = next_node
        next_node = next_node.succ
    graph.add_edge(current.id, next_node.id)

    nx.draw(graph, nx.circular_layout(graph), with_labels=False, node_size=0.2, arrowsize=4)
    plt.title(f"DHT")
    plt.savefig("graph.pdf", format='pdf')
    plt.clf()


def print_dht_circle_fingers(fingernode: 'NodeDHT') -> None:
    graph = nx.DiGraph()
    current = fingernode
    next_node = fingernode.succ

    while next_node != fingernode:
        graph.add_edge(current.id, next_node.id)
        current = next_node
        next_node = next_node.succ
    graph.add_edge(current.id, next_node.id)

    pos = nx.circular_layout(graph)
    for k, v in fingernode.ft.items():
        graph.add_edge(fingernode.id, v.id)
        # print("Adding {} -> {}".format(fingernode.id, v.id))
    nx.draw(graph, pos, with_labels=False, node_size=0.2, arrowsize=4)
    plt.title(f"Node {fingernode.name}'s finger table")
    plt.savefig("graph-fingers.pdf", format='pdf')
    plt.clf()
