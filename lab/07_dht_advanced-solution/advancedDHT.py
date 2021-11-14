from hashlib import sha256
from bitstring import BitArray
from tabulate import tabulate
import networkx as nx
import matplotlib.pyplot as plt

BITLENGTH = 32


def compute_key(string, bitlength=BITLENGTH):
    """Compute an hash digest BITLENGHT long and returns its integer value

    Args:
        string (str): the input for the hash function
        bitlength (int, optional): The length in bits of the hash output

    Returns:
        int: The integer resulting from the interpretation of the hash digest
        as an unsigned int in little endian notation
    """
    digest = sha256(bytes(string, 'utf-8')).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    return BitArray(bin=subbin).uint


def dist(a, b, maxnum=2**BITLENGTH - 1):
    """Compute the clockwise dist between a and b,
     given maxnum as max clock value"""
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)


def findNode(startnode, key):
    """Recursively find the node whose ID is the greatest
     but smaller ID in the DHT compared to key"""
    current = startnode
    recLevel = 0
    while dist(current.id, key) > \
            dist(current.succ.id, key):
        current = current.succ
        recLevel += 1
    #print("current {}, succ {}, key {}".format(current.id, current.succ.id, key))
    return current, recLevel


class NodeDHT():
    def __init__(self, name):
        self.name = name
        self.id = compute_key(name)
        self.succ = None
        self.pred = None
        self.ht = dict()
        self.finger = {}

    def setSuccessor(self, node):
        self.succ = node

    def setPredecessor(self, node):
        self.pred = node

    def store(self, key, value):
        responsible, _ = findNode(self, key)
        responsible.ht[key] = value

    def lookup(self, key):
        responsible, recLevel = findNode(self, key)
        try:
            value = responsible.ht[key]
            print("key: {} found! Value = {}".format(key, value))
            return value, recLevel
        except KeyError:
            print("{} not available in DHT".format(key))
            return None, recLevel

    def join(self, requester):
        responsible, _ = findNode(self, requester.id)

        requester.setPredecessor(responsible)
        requester.setSuccessor(responsible.succ)

        responsible.succ.setPredecessor(requester)
        responsible.setSuccessor(requester)

        # Rebalancing content distribution
        for k, v in responsible.ht.copy().items():
            newresp, _ = findNode(self, k)
            if newresp.id == requester.id:
                requester.store(k, responsible.ht[k])
                del responsible.ht[k]

    def leave(self):
        """The leaving node passes all its items to his predecessor,
        link also his pred with his succ"""
        self.pred.ht.update(self.ht)
        self.ht = dict()
        self.pred.setSuccessor(self.succ)
        self.succ.setPredecessor(self.pred)

    def update(self):
        myID = self.id
        for x in range(BITLENGTH):
            startFrom = self.finger[x] if x in self.finger else self
            #code.interact(local=dict(globals(), **locals()))
            fingerX, _ = findNode(startFrom, (myID + (2**x)) % (2**BITLENGTH))
            self.finger[x] = fingerX

    def findFinger(self, key):
        current = self
        for x in range(BITLENGTH):
            if dist(current.id, key) > \
                    dist(self.finger[x].id, key):
                current = self.finger[x]
        return current

    def fingerLookup(self, key):
        #print("Asking key: {} to node: {}".format(key, self.id))
        current = self.findFinger(key)
        nextNode = current.findFinger(key)
        recLevel = 0
        while dist(current.id, key) > \
                dist(nextNode.id, key):
            #print("Finger: {}, succ.Finger: {}".format(current.id, nextNode.id))
            current = nextNode
            nextNode = current.findFinger(key)
            recLevel += 1

        try:
            value = current.ht[key]
            print("key: {} found! Value = {}".format(key, value))
            return value, recLevel
        except KeyError:
            print("{} not available in DHT".format(key))
            return None, recLevel


def printName2ID(nodelist):
    for n in nodelist:
        print("{} -> {}".format(n.name, n.id))


def printRing(startnode):
    nodelist = [startnode.id]
    nextNode = startnode.succ
    while (nextNode != startnode):
        nodelist.append(nextNode.id)
        nextNode = nextNode.succ
    nodelist = sorted(nodelist)
    print(" -> ".join([str(x) for x in nodelist]))


def printDHT(startnode, fmt='pretty'):
    node2content = {startnode.id: startnode.ht}
    nextNode = startnode.succ
    while (nextNode != startnode):
        node2content[nextNode.id] = nextNode.ht
        nextNode = nextNode.succ
    tabulable = {k: sorted(list(v.items()))
                 for k, v in sorted(node2content.items())}
    return tabulate(tabulable, headers='keys', tablefmt=fmt)


def wordsOfFile(file):
    words = []
    with open(file, 'r') as file:
        for line in file:
            for word in line.split():
                words.append(word)
    return words


def drawCircularDHT(startnode):
    G = nx.DiGraph()
    current = startnode
    nextNode = startnode.succ
    while(nextNode != startnode):
        G.add_edge(current.id, nextNode.id)
        current = nextNode
        nextNode = nextNode.succ
    G.add_edge(current.id, nextNode.id)
    nx.draw(G, nx.circular_layout(G), with_labels=False, node_size=0.1)
    plt.show()
    plt.clf()


def drawCircularWithFinger(fingernode):
    G = nx.DiGraph()
    current = fingernode
    nextNode = fingernode.succ
    #print("Fingernode: {}".format(fingernode.id))
    while(nextNode != fingernode):
        G.add_edge(current.id, nextNode.id)
        current = nextNode
        nextNode = nextNode.succ
    G.add_edge(current.id, nextNode.id)
    pos = nx.circular_layout(G)
    for k, v in fingernode.finger.items():
        G.add_edge(fingernode.id, v.id)
        #print("Adding {} -> {}".format(fingernode.id, v.id))
    nx.draw(G, pos, with_labels=False, node_size=20, arrowsize=5)
    plt.title("circular DHT with finger links of node {}".format(fingernode.name))
    plt.savefig("dhtGraphWithFingers.pdf", format='pdf')
    plt.clf()


