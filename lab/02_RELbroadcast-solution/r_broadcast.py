import networkx as nx
import random
import matplotlib.pyplot as plt
from argparse import ArgumentParser

from EventScheduler import EventScheduler
from MyProcess import MyProcess

parser = ArgumentParser()
parser.add_argument("-l", "--lossP", dest="lossP", default=0.0, action="store", type=float)
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


def simulate_r_broadcast(G, processes, sched):

    # Initialize simulation picking random first transmitter
    src = random.choice(list(G.nodes()))
    msg = random.randint(0, 1000)

    others = list(set(G.nodes() - {src}))
    
    print("START simulation")
    # Create first events to be place in the event queue :)
    processes[src].r_broadcast(msg, others, time=0)

    while (len(sched.queue) > 0):
        # some process should simulate reception
        src, dest, msg = sched.pop_event()
        print("TIME={:.3f}: {} --[{}]--> {}".format(sched.elapsed_time(), src, msg, dest))
        processes[dest].on_receive(src, msg, time=sched.elapsed_time())

    # Out of the loop... means no more "send" event left to process
    print("END simulation")


def main():
    args = parser.parse_args()

    sched = EventScheduler()

    # Check out seqdiag 
    # http://blockdiag.com/en/seqdiag/introduction.html
    outputDiag = open("mySequenceDiag.diag", 'w')
    outputDiag.write("{\n")
    outputDiag.write("\tactivation = none;\n")

    # create the network
    N = 5
    G = nx.complete_graph(N)
    processes = [MyProcess(id, sched, G, outputDiag) for id in range(N)]

    # Set Link Model
    fair_loss(G, lossP=args.lossP)

    # Set Nodes Failure Model
    stop_failure(G, args.crashP)

    # Set nodes initial color
    nx.set_node_attributes(G, "red", "color")

    # Draw graph before Broadcast
    drawgraph(G, "Before broadcast")

    # Simulate Reliable Broadcast
    simulate_r_broadcast(G, processes, sched)

    # Redraw after broadcast
    drawgraph(G, "After broadcast")

    outputDiag.write("}\n")
    outputDiag.close()


if __name__ == '__main__':
    main()
