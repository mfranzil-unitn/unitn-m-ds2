import random
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

FINITE_DUPLICATION = 100

parser = ArgumentParser()
parser.add_argument("-l", "--lossP", dest="lossP",
                    default=0.0, action="store", type=float)
parser.add_argument("-r", "--repP", dest="repP",
                    default=1.0, action="store", type=float)
parser.add_argument("-c", "--crashP", dest="crashP",
                    default=0.0, action="store", type=float)


def fair_loss(G, lossP=0.0, repP=1.0):
    nx.set_edge_attributes(G, lossP, "lossP")
    nx.set_edge_attributes(G, repP, "repP")


def stop_failure(G, crashP=0.0):
    nx.set_node_attributes(G, crashP, "crashP")


def drawgraph(G, title):
    plt.title(title)
    nx.draw(G, node_color=list(nx.get_node_attributes(
        G, "color").values()), labels=nx.get_node_attributes(G, "RCV"))
    plt.show()


def deliver(G, dest, color):
    G.nodes[dest]["color"] = color
    G.nodes[dest]["RCV"] += 1


def send(G, source, dest, color):
    # Simulate channel conditions!

    # First simulate loss
    if random.random() < G[source][dest]['lossP']:
        print("\tLost packet over {}--{} link".format(source, dest))
        return

    # if not lost then it may be repeated...
    num_rep = 0
    for _ in range(FINITE_DUPLICATION):
        if random.random() < G[source][dest]['repP']:
            num_rep += 1

    # Simulate delivery
    for _ in range(num_rep):
        deliver(G, dest, color)


def beb(G):
    # Choose initial node/process (called p)
    p = random.choice(list(G.nodes()))

    # Random color as message, we draw in that color nodes that deliver the message
    rc = '#%02x%02x%02x' % tuple(np.random.randint(256, size=3))

    for n in set(set(G.nodes()) - {p}):
        print("Sending message from {} --> {}".format(p, n))
        # Simulate crash during sending operation
        if random.random() > G.nodes[p]["crashP"]:
            send(G, p, n, rc)
        else:
            print("Node {} crashed!!!".format(p))
            return


def main():
    args = parser.parse_args()

    # create the network
    G = nx.complete_graph(40)

    # Set Link Model
    fair_loss(G, lossP=args.lossP, repP=args.repP)

    # Set Nodes Failure Model
    stop_failure(G, args.crashP)

    # Set nodes initial color and RCVcounter
    nx.set_node_attributes(G, "red", "color")
    nx.set_node_attributes(G, 0, "RCV")

    # Draw graph before Broadcast
    drawgraph(G, "Before broadcast")

    # Simulate Best-Effort Broadcast
    beb(G)

    # Redraw after broadcast
    drawgraph(G, "After broadcast")


if __name__ == '__main__':
    main()
