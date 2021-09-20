# Reliable Broadcast

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

## Reliability modes

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

## Message ordering

This is the same stuff seen in Distributed Systems 1. As usual we have our six flavours (adding uniform ones as before, when all processes must deliver - not just the corerct ones - leading up to twelve).

A *broadcast transformation* is an algorithm that strengthens a weaker broadcast algorithm. A transformation is an algorithm $T_{a > b}$ that converts any algorithm A solving A into an algorithm B solving B. It must also preserve some properties.

In particular, we must make sure that no messages are created and never re-delivered.

Finally, some of them may be called blocking if some runs have delayed delivery of messages.

## Atomic broadcast and consensus

These two problems are equivalent, that is, there is both a transformation from one to the other and vice versa. In this case, the proposal phase of consensus can be visualized as an Atomic-broadcast, and on delivery, the decision flag goes to true. On the other hand, peers propose values by broadcasting their current set of unordered items, and upon a decision request they deliver their received messages.