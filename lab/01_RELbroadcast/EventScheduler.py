import heapq


class EventScheduler:
    def __init__(self):
        self.queue = []
        self.time = 0
        self.last = 0

    def schedule_event(self, interval, e):
        t = self.time + interval
        if t > self.last:
            self.last = t
        heapq.heappush(self.queue, (t, e))

    def pop_event(self):
        e = heapq.heappop(self.queue)
        self.time = e[0]
        return e[1]

    def elapsed_time(self):
        return self.time

    def last_event_time(self):
        return self.last
