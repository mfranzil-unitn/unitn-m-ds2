
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

I was bored, so I stopped taking notes. It is easy, look at the slides