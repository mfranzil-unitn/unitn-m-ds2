from advancedDHT import *
import code  # code.interact(local=dict(globals(), **locals()))

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
    niceQuote = """nel mezzo del cammin di nostra vita mi
         ritrovai per una selva oscura che la diritta via era smarrita"""
    contents = niceQuote.split(" ")
    contents = [w.strip() for w in contents if w]
    for word in contents:
        key = compute_key(word)
        node = random.choice(nodes)

        node.store(key, word)

    print("Print DHT after 4 nodes inserted plus Divine Comedy content")
    print(printDHT(n1))
    
    print("TEST LOOKUP QUERIES")
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



    print("TEST CONTENT PASSING DURING JOIN")
    print("Add one node and check restructuring of DHT")
    print("DHT BEFORE JOIN -->")
    print(printDHT(n1))
    n7 = NodeDHT("node7")
    n1.join(n7)
    nodes.append(n7)
    print("DHT AFTER JOIN -->")
    print(printDHT(n1))


    # Example of leaving, check DHT after leaving
    print("TEST CONTENT PASSING DURING LEAVE")
    print("Make one node leave and check restructuring of DHT")
    print("DHT BEFORE LEAVE -->")
    print(printDHT(n1))
    n4.leave()
    nodes.remove(n4)
    del n4
    print("DHT AFTER LEAVE -->")
    print(printDHT(n1))

    print("NOW ADDING more nodes and 1000 more items")
    # Now add a lot more nodes, then add more contents
    for i in range(10, 100):
        newnode = NodeDHT("node"+str(i))
        n1.join(newnode)
        nodes.append(newnode)

    # Now add many nodes and more contents, read by a file
    moreWords = wordsOfFile("lipsum.txt")
    for word in moreWords:
        key = compute_key(word)
        node = random.choice(nodes)
        node.store(key, word)

    print("Saving large DHT in html")
    tablehtml = open("table.html", 'w')
    html = printDHT(n1, 'html')
    tablehtml.write(html)
    tablehtml.close()

    print("COMPUTING FINGER TABLES FOR ALL NODES")
    for n in nodes:
        n.update()

    print("SAVING DHT GRAPH WITH FINGER LINKS OF node1")
    drawCircularWithFinger(n1)

    print("COMPARE #STEPS FINGERLOOKUP VS STANDARD LOOKUP")

    tabulable = [["content", "fingerSteps", "standardSteps"]]
    for word in contents:
        key = compute_key(word)
        found, fsteps = n1.fingerLookup(key)
        found, stdsteps = n1.lookup(key)
        tabulable.append([word, fsteps, stdsteps])
    print(tabulate(tabulable, headers="firstrow", tablefmt='pretty'))
    



if __name__ == "__main__":
    main()
