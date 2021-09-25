import random
from EventScheduler import EventScheduler

class MyProcess():
    def __init__(self, id, sched, G, out):
        self.id = id
        self.sched = sched
        self.G = G
        self.out = out
        self.crashed = False
        self.delivered = set()

    def log(self, src, dest, label, options=[]):
        if options:
            optstring = ",".join(options)+','
        else:
            optstring = ""
        self.out.write(
            "\t{} -> {} [{}label = \"{}\"];\n".format(src, dest, optstring, label))

    def create_send_event(self, dest, msg):
        return (self.id, dest,  msg)

    def crash(self, time):
        print("\t{} crashed!".format(self.id))
        self.crashed = True
        self.G.nodes[self.id]['color'] = 'orange'
        self.log(self.id, self.id, "TIME: {:.2f}".format(time), ["failed"])

    def r_broadcast(self, msg, dests, time):
        print("{} r-sending to: {}".format(self.id, dests))

        for q in dests:
        # Try to send to all destinations processes
        # For all q in dests...
            # simulate crash of sender before transmitting
            if random.uniform(0, 1) < self.G.nodes[self.id]['crashP']:
                self.crashed = True

            if not self.crashed:
                # send msg to q by creating related "send event"
                ev = self.create_send_event(q, msg)
                # remember to schedule the event!!!
                self.sched.schedule_event(time + random.random(), ev)
            else:
                self.crash(random.randint(1, 10))
                return
                #... i.e., if crashed:
                # logic of crashing and stop the r-broadcasting
                # NB: check out (and use) crash() method of this class
        self.deliver(msg, time)
        # end of the SEND TO ALL routine, time to DELIVER, only if not crashed!!!
        # NB: check out and use deliver() method


    def on_receive(self, src, msg, time):
        if self.crashed:
            return

        # Do not process message if already crashed

        if random.uniform(0, 1) < self.G[src][self.id]["lossP"]:
            self.log(src, self.id, "TIME: {:.2f}".format(time), ["failed", "diagonal"])
            return
        else:
        # Simulate link failure (as for BEB...)
        # if packet not lost:
            # Here we got the message...
            # A log statement for logging the reception of a message provided as example :)
            self.log(src, self.id, "TIME: {:.2f}".format(time), ["diagonal"])
            if msg in self.delivered:
                pass
            else:
                dests = list(set(set(self.G.nodes()) - {src}) - {self.id})
                self.r_broadcast(msg, dests, time)
            # if message already delivered...
                # dont do anything if already have the message
                # use the delivered{} attribute of this Process instance to keep track of received messages
            # Otherwise re-propagate message to all but not source node (and not to itself)    
            # logic of flooding here
        # but if packet was actually lost...
            # packet lost logic (just log the loss event)

    def deliver(self, msg, time):
        if msg not in self.delivered:
            self.delivered.add(msg)
            print("\t{} delivered MSG: {}".format(self.id, msg))
            self.G.nodes[self.id]['color'] = 'blue'
            self.log(self.id, self.id, "TIME: {:.2f} DELIVERED".format(time))
