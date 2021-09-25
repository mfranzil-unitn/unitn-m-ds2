import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser

FINITE_DUPLICATION = 100

parser = ArgumentParser()
parser.add_argument("-l", "--lossP", dest="lossP", default=0.0, action="store", type=float)
parser.add_argument("-r", "--repP", dest="repP", default=1.0, action="store", type=float)
parser.add_argument("-c", "--crashP", dest="crashP", default=0.0, action="store", type=float)


def fair_loss(G, lossP=0.0, repP=1.0):
    nx.set_edge_attributes(G, lossP, "lossP")
    nx.set_edge_attributes(G, repP, "repP")


def stop_failure(G, crashP=0.0):
    nx.set_node_attributes(G, crashP, "crashP")


def drawgraph(G, title):
    plt.title(title)
    nx.draw(G, node_color=list(nx.get_node_attributes(G, "color").values()), labels=nx.get_node_attributes(G, "RCV"))
    plt.show()


def deliver(G, dest, color):
    G.nodes[dest]["color"] = color
    G.nodes[dest]["RCV"] += 1


def send(G, source, dest, color):
    # Simulate channel conditions!

    # First simulate loss
    if random.uniform(0, 1) < G[source][dest]["lossP"]:
        print(f"Message {source} -> {dest} lost!")
        return

    # if not lost then it may be repeated...
    rep_c = 0
    for i in range(FINITE_DUPLICATION):
        if random.uniform(0, 1) < G[source][dest]["repP"]:
            rep_c += 1
            #print(f"Message {source} -> {dest} repeated!")

    # Simulate delivery
    for i in range(rep_c):
        deliver(G, dest, color)

    print(f"Message {source} -> {dest} OK!")


def beb(G):
    # Choose initial node/process (called p)
    p = random.choice(list(G.nodes()))

    # Random color as message, we draw in that color nodes that deliver the message
    rc = '#%02x%02x%02x' % tuple(np.random.randint(256, size=3))
    
    # For all processes (graph nodes) but me...
    # Simulate send to that process/node
    for i in set(set(G.nodes()) - {p}):
        if random.uniform(0, 1) > G.nodes[p]["crashP"]:
            send(G, p, i, rc)
        else:
            print(f"Node {p} crashed!")
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
    #drawgraph(G, "Before broadcast")

    # Simulate Best-Effort Broadcast
    beb(G)

    # Collect average reception rate:
    med = []
    for index in list(G.nodes):
        med.append(G.nodes[index]["RCV"])

    print(f"Average reception rate: {sum(med) / (len(med) - 1)}")

    # Redraw after broadcast
    #drawgraph(G, "After broadcast")


if __name__ == '__main__':
    main()
