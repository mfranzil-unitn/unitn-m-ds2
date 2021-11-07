import hashlib
from tabulate import tabulate
import code  # code.interact(local=dict(globals(), **locals()))
import random

BITLENGHT = 8


def compute_key(string, bitlength=BITLENGHT):
    digest = hashlib.sha256(bytes(string, 'utf-8')).digest()
    subdigest = digest[:bitlength//8]
    return int.from_bytes(subdigest, 'little')


def clock_dist(a, b, maxnum=2**BITLENGHT - 1):
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)


class NodeDHT():
    def __init__(self, name):
        self.name = name
        self.id = compute_key(name)
        self.succ = None
        self.pred = None
        self.ht = dict()

    def setSuccessor(self, node):
        self.succ = node

    def setPredecessor(self, node):
        self.pred = node

    def join(self, requester):
        requesterID = requester.id
        dist = clock_dist(self.id, requesterID)
        distFromMySuccessor = clock_dist(self.succ.id, requesterID)

        if dist > distFromMySuccessor:
            self.succ.join(requester)
        else:
            requester.setPredecessor(self)
            requester.setSuccessor(self.succ)

            self.succ.setPredecessor(requester)
            self.setSuccessor(requester)

    def store(self, key, value):
        dist = clock_dist(self.id, key)
        distFromMySuccessor = clock_dist(self.succ.id, key)

        if dist > distFromMySuccessor:
            # Forward going closer to responsible node
            self.succ.store(key, value)
        else:
            self.ht[key] = value

    def lookup(self, key):
        print("node: {} looking for key: {}".format(self.id, key))
        dist = clock_dist(self.id, key)
        distFromMySuccessor = clock_dist(self.succ.id, key)

        if dist > distFromMySuccessor:
            # Forward going closer to responsible node
            self.succ.lookup(key)
        else:
            try:
                value = self.ht[key]
                print("key: {} found! Value = {}".format(key, value))
                return value
            except KeyError:
                print("{} not available in DHT".format(key))
                return None


def printRing(startnode):
    nodelist = [startnode.id]
    nextNode = startnode.succ
    while (nextNode != startnode):
        nodelist.append(nextNode.id)
        nextNode = nextNode.succ
    nodelist = sorted(nodelist)
    print(" -> ".join([str(x) for x in nodelist]))


def printDHT(startnode):
    node2content = {startnode.id: startnode.ht}
    nextNode = startnode.succ
    while (nextNode != startnode):
        node2content[nextNode.id] = nextNode.ht
        nextNode = nextNode.succ
    tabulable = {k: sorted(list(v.items()))
                 for k, v in sorted(node2content.items())}
    print(tabulate(tabulable, headers='keys'))


def main():
    # start a network with 4 random nodes

    # start first 2 nodes setting manually succ and pred.

    print("Creating first two nodes")
    n1 = NodeDHT("node1")
    n2 = NodeDHT("node2")

    n1.setSuccessor(n2)
    n1.setPredecessor(n2)
    n2.setSuccessor(n1)
    n2.setPredecessor(n1)

    print("Creating further two nodes")
    # add 2 more nodes by join procedure
    n3 = NodeDHT("node3")
    n4 = NodeDHT("node4")

    print("n3 joining from n2")
    n2.join(n3)

    print("n4 joining from n1")
    n1.join(n4)

    nodes = [n1, n2, n3, n4]

    # Inject some contents
    niceQuote = "nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura che la diritta via era smarrita"
    contents = niceQuote.split(" ")
    for word in contents:
        key = compute_key(word)
        node = random.choice(nodes)

        node.store(key, word)

    printDHT(n1)
    code.interact(local=dict(globals(), **locals()))

    # Test lookups queries

    # Correct queries
    for _ in range(4):
        c = random.choice(contents)
        node = random.choice(nodes)

        print("Searching for \'{}\'".format(c))
        node.lookup(compute_key(c))
        print("\n")

    # Wrong query
    c = "NOT INSERTED UNLESS HASH CONFLICT XD"
    print("Searching for \'{}\'".format(c))
    n1.lookup(compute_key(c))


if __name__ == "__main__":
    main()
