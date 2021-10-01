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
            # simulate crash of sender
            print("\t{} --attempt--> {}".format(self.id, q))
            if not self.crashed:
                if random.random() > self.G.nodes[self.id]['crashP']:
                    ev = self.create_send_event(q, msg)
                    self.sched.schedule_event(time + random.random(), ev)
                else:
                    self.crash(time=time)
                    return
        if not self.crashed:
            self.deliver(msg, time)

    def on_receive(self, src, msg, time):
        # Do not process message if already crashed
        if self.crashed:
            return
        # Simulate link failure
        if random.random() > self.G[src][self.id]['lossP']:
            # Here we got the message
            self.log(src, self.id, "TIME: {:.2f}".format(time), ["diagonal"])
            if msg in self.delivered:
                # dont do anything if already have the message
                return
            others = list(set(self.G.nodes() - {self.id, src}))
            self.r_broadcast(msg, others, time)
        else:
            # packet lost
            self.log(src, self.id, "TIME: {:.2f}".format(time), ["failed", "diagonal"])
            return

    def deliver(self, msg, time):
        if msg not in self.delivered:
            self.delivered.add(msg)
            print("\t{} delivered MSG: {}".format(self.id, msg))
            self.G.nodes[self.id]['color'] = 'blue'
            self.log(self.id, self.id, "TIME: {:.2f} DELIVERED".format(time))
