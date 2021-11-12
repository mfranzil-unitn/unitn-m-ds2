import random

from advancedDHT import *

MAX_NODES = 24


def main_old():
    # start a network with n random nodes

    # start first 2 nodes setting manually succ and pred.
    n0, n00 = NodeDHT("n0"), NodeDHT("n00")
    nodes = [n0, n00]

    n0.set_successor(n00)
    n0.set_predecessor(n00)

    n00.set_successor(n0)
    n00.set_predecessor(n0)

    for i in range(1, 5):
        n = NodeDHT("node" + str(i))
        n0.join(n)
        nodes.append(n)

    # Inject some contents
    niceQuote = "nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura che la diritta via era smarrita"
    contents = niceQuote.split(" ")
    for word in contents:
        key = compute_key(word)
        node = random.choice(nodes)

        node.store(key, word)

    # code.interact(local=dict(globals(), **locals()))

    print_ring(n0)
    print_dht(n0)

    # Test lookups queries

    # Correct queries
    for _ in range(4):
        sample = random.choice(contents)
        node = random.choice(nodes)

        print(f"Searching for \'{sample}\'")
        node.lookup(compute_key(sample))

    # Wrong query
    sample = "NOT INSERTED UNLESS HASH CONFLICT XD"
    print("Searching for \'{}\'".format(sample))
    n0.lookup(compute_key(sample))

    # Test removal
    sample = random.sample(contents, 10)
    for i in sample:
        node = random.choice(nodes)

        print(f"Deleting \'{i}\' (key: {compute_key(i)})")
        value = node.remove(compute_key(i))

    contents = [i for i in contents if i not in sample]

    print_dht(n0)

    n0.leave()
    del n0

    print_dht(n00)

    na = NodeDHT('NodeA')

    n00.join(na)
    nodes += [na]

    print_dht(n00)


def main_new():
    n0, n00 = NodeDHT("n0"), NodeDHT("n00")
    nodes = [n0, n00]

    n0.set_successor(n00)
    n0.set_predecessor(n00)

    n00.set_successor(n0)
    n00.set_predecessor(n0)

    # Now add a lot more nodes, then add more contents
    for i in range(10, MAX_NODES):
        newnode = NodeDHT("node" + str(i))
        n00.join(newnode)
        nodes.append(newnode)

    # Now add many nodes and more contents, read by a file
    contents = []
    ctr = 0
    with open('poe.txt') as poe:
        for line in poe:
            for word in line.split():
                ctr += 1
                word.replace(",", "") \
                    .replace(";", "") \
                    .replace(".", "") \
                    .replace("!", "") \
                    .replace("'", "") \
                    .replace("?", "") \
                    .replace("-", "") \
                    .replace("(", "") \
                    .replace(")", "") \
                    .replace("[", "") \
                    .replace("]", "") \
                    .lower()
                contents.append(word)
                key = compute_key(word)
                node = random.choice(nodes)
                node.store(key, word)

    print("Saving large DHT in html")
    tablehtml = open("table.html", 'w')
    html = print_dht(n0, 'html')
    tablehtml.write(html)
    tablehtml.close()

    # Compute finger tables
    for n in nodes:
        n.update()

    # Drawing graph
    print_dht_circle(n00)
    print_dht_circle_fingers(n00)

    # Comparison
    tabulable = [["content", "fingerSteps", "standardSteps"]]
    for word in contents:
        key = compute_key(word)
        found, fsteps = n0.finger_lookup(key)
        found, stdsteps = n0.lookup(key)
        tabulable.append([word, fsteps, stdsteps])
    print(tabulate(tabulable, headers="firstrow", tablefmt='pretty'))

    # In the proposed solution for the main file
    # 1. (initDHT) -> printDHT -> Create new node and JOIN -> printDHT -> make one
    # node LEAVE -> printDHT; so you check content passing works properly
    # 2. Add up to 100 nodes and 1000 items -> printDHThtml -> drawCircularGraph NB: BITLENGTH >> 8 or may have hash conflicts!!!
    # • Check graph is truly circular ^ check from html that content is fairly distributed 3. Compute finger table for each node -> drawGraphWithFingerLinks4someNode 4. Issue many fingerLookups and standard lookups
    # • keep track of recursionLevel (how many forwardings)
    # • compare the recursionLevel for same key looked up with/without finger- table... who performs better???


if __name__ == "__main__":
    main_new()
