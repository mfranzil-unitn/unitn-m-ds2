
# DS2 notes
## 202109xx Reliable Broadcast

Appl. Protocol -> Broadcast Protocol -> NETWORK
                                         || ||
Appl. Protocol -> Broadcast Protocol <- NETWORK

- Asyncronous systems
- No byzantine failures, only crashes
- Correct process -> if it doesn't fail

Two failure modes:

- No failures: if the sender crashes and you sent the message, the message will somehow arrive to the destination.
- Perfect Channels: both sender and destination must be correct and the message will eventually arrive

Underlying network:

- Complete graph: abstraction in which everyone can talk with everybody else
- Point to point: process canonly communicate with neighbors (common in big DS in which it's more efficient to just contact a small subset of processes, e.g. if there are too many and too dynamic IP addresses)

### Reliability modes

> *B*est-effort broadcast

- if p, q are correct then every message *B*-broadcasted by p is eventually *B*-delivered by q
- m is *B*-delivered by a process at most once, and only if it was broadcast (no correct assumption!!!)

This protocol works with Perfect Channels (and also with No Failures). However, if the sender crashes before completing the multicast, some of them will not deliver the message.

> *R*eliable broadcast

- if a correct process brodcasts m, then it eventually delivers m (locally)
- m is delivered by a process at most one, and only if it was previously broadcast (as before)
- if a correct (!!) process delivers m, then all correct process will eventually deliver m.

When we say that a process crashes, we mean that it will _eventually_ crash. So we don't care when, just that it will. In this case, if a process crashes then we now don't care and it's not correct anymore.

> *U*niform reliable broadcast

This is basically the same as the other one, but now the agreement says that if _a_ process delivers then all correct ones will deliver a message.

The previous algorithm still implements this broadcast, although the assumptions change: we cannot have communication failures, so that we cannot use of the No Failures mode.

### Message ordering

This is the same stuff seen in Distributed Systems 1. As usual we have our six flavours (adding uniform ones as before, when all processes must deliver - not just the corerct ones - leading up to twelve).

A *broadcast transformation* is an algorithm that strengthens a weaker broadcast algorithm. A transformation is an algorithm $T_{a > b}$ that converts any algorithm A solving A into an algorithm B solving B. It must also preserve some properties.

In particular, we must make sure that no messages are created and never re-delivered.

Finally, some of them may be called blocking if some runs have delayed delivery of messages.

### Atomic broadcast and consensus

These two problems are equivalent, that is, there is both a transformation from one to the other and vice versa. In this case, the proposal phase of consensus can be visualized as an Atomic-broadcast, and on delivery, the decision flag goes to true. On the other hand, peers propose values by broadcasting their current set of unordered items, and upon a decision request they deliver their received messages.

## 20210927 - Data dissemintation

Efficiency, robustness and speed when scaling the distribution of large amount of data -> flooding (inefficient since it's O(n^2)), tree (but fragile, although O(n)), gossip (efficient and robust O(nlogn), but with high latency).

We consider the total number of messages sent by all and by each node.

We now change approach, using a probabilistic one. We do not have deterministic guarantees on reliability. THe idea behind epidemic protocols is that we can have fast ones (flood, tree), efficient (gossip, tree) or robust (flood, gossip), but not all three.

Our basic assumptions is that we are in a asynchronous system where the processes fail by crashing and the network can lose messages, but not corrupt or duplicate them. Assume we have a single-data database (applying it to multiple data is the same). Our goal is to drive the system towards eventual consistency (aka eventually all nodes will obtain the same copy of the database)

### Probabilistic broadcast

The probabilistic broadcast is an algorithm in which unlike BE-B, when a node sends a message to another one and both are correct, there is a probability that such a message will eventually be PB-delivered with probability p'. This may happen at most once (as we said before).

This algorithm works under some strong assumptions (i.e. every node can communicate with each other and they know the graph; costs are homogeneous)

### Epidemic model

The SIR model allows three types of node status:

- Susceptible -> if p has not been yet infected
- Infective -> if p has been infected and can spread the disease
- Remove -> if p has been infected but is now healthy again

These ideas can be easily applied to DSs.

### Direct mail algorithm

This algorithm notifies ALL nodes as soon as an update arrives. Vice-versa, receiving nodes check if incoming updates apply to them.

### Anti-entropy algorithm

In this case, each node chooses another node at random at resolves DB differences with them. It is divided in rounds of length $\Delta$, in which each node can contact one node, and can be contacted by several ones. We see three different approaches:

- Push-based: only contacting nodes can send data
- Pull-based: nodes contacting ask the recipient for dat
- Push-pull-based: a combination of the above

See the slides for the compartmental mode analysis, which features the calculations of the probabilities. In particular, at round t+1, given that s0 = n - 1 / n (that is, the initial probability of being susceptible is 1 - (1/n), since 1/n is the probability of being infective, aka the first node). The expected number of probability that a node may be susceptible with the pull approach is st^2, since we have at round t a probability st multiplied for the probability that that very node may remain suceptible (so st again). On the other hand, with the push approach, we multiply st (probability of being susceptible) with (1-1/n) (probability that an infective node contacts him) all to the power of n(1-st) (multip,lied for each possible infective node)

### Rumor mongering 

In rumor mongering, nodes are initially susceptible, as usual. When a node receives an update it becomes infective, and starts spreading the rumor incontrollably: every set amount of time, it sends such rumor to a node. When the hype dies off, the node will lose interest in spreading the rumor and become removed. This approach is doable for one or more updates. In order to decide the policy of loss of interest, one can decide:

- When: Counter vs coin (random)
  - Coin (random): lose interest with probability 1/k
  - Counter: lose interest after k contacts
- Why: Feedback vs blind
  - Feedback: lose interest only if the recipient knows the rumor.   - Blind: lose interest regardless of the recipient.

Rumor mongering can be mixed with anti-entropy: for example, new updates can be spread quickly with rumor mongering; however, since there is no guarantee that everyone will receive the update, an anti-entropy protocol can be run in the background in order to let eventually know everyone of the update.

Finally, we can use death certificates in order to deal with deletions (i.e. deleted updates). DCs can be either retained until we are sure the whole system has gotten them, or discard them after a prolonged amount of time.

## 20211004, 20211011

Notes for these two lessons can be found in the `consensus.pdf` file.

## 20211018

### P2P

Brief introduction on overlay networks and their role in big distributed systems, especially in P2P - which are inherently mutable and decentralized. While alternative topologies exist (e.g. hierarchical, semi-decentralized, structured such as DHT, and other random ones). P2P has its strength in using the power of edge nodes to send and receive that in order to benefit both the sender and the receiver.

In this section, we analyze DHT (Distributed Hash Tables). We saw them in DS1, so I do not write any superfluous notes for them.

Indeed, the first thing unseen with DHTs regards routing. Suppose we have a DS, in which every machine has the task of maintaining a set amount of keys. Any machine that needs to reach such server (e.g. that needs to do a put on key "x"), can first contact a server which is nearer to the location, which will recursively contact another one, and so on.

Talking more explictly, our system is structured as follows:

- keys and nodes are represented with nodes strictly pertaining to an ID space (usually keys are hashes, node identifiers are random hashes). A large enough space allows for sufficiently low probabilities of collisions
- each node in the DHT stores k,v pairs. Authority on the nodes is ensured by storing them such that their identifier of node n is the closest to each of its keys k, and the largest node id smaller than k.
- build an overlay network, in which each node has both immediate and long range neighbors
- allow for both recursive and iterative routing in order to maintain robustness and latency low

It is also important to recover from failures (as eventually there will be no neighbors) and allow new nodes to join the system properly. Recovery can be either reactive (when other neighbors notice a crash) and proactive (by regular sending of a neighbor list).

Some algorithms seen in class include:

- Chord: already seen in DS1...just remember about space, O(log n) routing, and the join procedure - in which each node sends a \<stabilize\> message to successors and \<notify\> to precedecssors
- CAN - associates to each node and item an d-dimensional ID in a d-dimensional torus. The routing table size is constant with regards to the dimension d. Brief explaination about the subdivision of spaces (i.e. when a node joins, it is moved into an empty space and the space itself sliced in a rectangular area 2:1)
- Kademlia - tree-based routing in which every node maintaing information about keys close to itself and parallel async queries are used. Nodes are treated as leafs, so for each leaf, there will be a number of discrete subtrees which will either have no common prefix or part of a common prefix. This information is used in routing in order to incrementally advance the distance to the searched key.

## 20211024

### Security aspects of DHTs

When considering DHTs, we must take care of security aspects that may impact the system, such as:

- Sybil attacks: when an attacker introduces bogus nodes that do not adhere to protocols. To defend, we can use centralized certifications, computational puzzles, and registration, although they are impossible to completely destroy
- Eclipse attacks: when an attacker tries to corrupt routing tables of honest nodes by redirecting them to malicius nodes. Is defendable by constraining the neighbor selection.
- Routing and storage attacks: various attacks taht may be mitigated with redundancy.

### Unstructured systems

Finally, we visualize two systems that come with great drawbacks due to their design.

- Gnutella: a protocol for peer-to-peer research. Each node selects its own neighbors and sends up to five types of messages. They include PING, PONG, QUERY, QUERYHIT, and PUSH. The first two make up half of Gnutella traffic, overcrowding the network with useless messages. Moreover, we have no control on how the network is actually generated. Gnutella was a failure, and although a pioneer on decentralization, suffered from being continuously patched and not being reliable and efficient.
- BitTorrent: a P2P file sharing protocol. It is designed for efficient content download. Its structure is based on a torrent file, a dictionary that contains a tracker, a name, the number of pieces, the hash, and the number of bytes per pieces. BitTorrent performs both peer selection (where to upload pieces) and piece selections (what to download). Usually, either priority is given to missing sub-pieces or to the rarest pieces on the network. Other policies including random first piece or endgame mode. Regarding peer selection, choking is a temporary refusal to upload, used against peers that leech data without contributing, in order to assure that as many peers as possible open dual connections for both upload and download. 

Please see the slides for more information about BitTorrent specifics.

## 20211029

### Complex Systems, Peer Sampling (epidemics)

The lecture started with an overview on some definitions about graphs, including average path length, induced graphs, and clustering coefficients.

Due to the vast amount of small definitions, it is recommended to see the slides instead. No notes were taken.

- clustering coefficient = probability

## 20211108

From this point, no further notes were taken.

