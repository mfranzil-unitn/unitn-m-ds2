import hashlib

BITLENGTH = 8


def compute_key(string: str, bitlength=BITLENGTH):
    """
    Compute a key from a string.
    """
    digest = hashlib.sha256(bytes(string, 'utf-8')).digest()
    subdigest = digest[:bitlength // 8]
    return int.from_bytes(subdigest, 'little')


def clock_dist(a: int, b: int, maxnum=2 ** BITLENGTH - 1):
    """
    Compute the distance between two keys.
    """
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)


class NodeDHT:
    """
    Node in a DHT. With name, ID (address), pointers to successor and pred, storage (an HT)
    """

    def __init__(self, _id: str):
        self.name = _id
        self.id = compute_key(_id)
        self.pred = None
        self.succ = None
        self.storage = {}

    def set_successor(self, succ: 'NodeDHT'):
        self.succ = succ

    def set_predecessor(self, pred: 'NodeDHT'):
        self.pred = pred

    def join(self, joiner: 'NodeDHT'):
        """
        Join two nodes. A -> X -> B or B -> X -> A
        """
        if clock_dist(self.id, joiner.id) > clock_dist(self.succ.id, joiner.id):
            self.succ.join(joiner)
        else:
            joiner.set_predecessor(self)
            joiner.set_successor(self.succ)
            self.succ.set_predecessor(joiner)
            self.set_successor(joiner)

    def store(self, value):
        key = compute_key(value)
        if key == self.id or (self.id - key) % (2 ** BITLENGTH) < (self.id - self.pred.id) % (2 ** BITLENGTH):
            # if clock_dist(self.id, key) > clock_dist(self.succ.id, key):
            self.storage[key] = value
            return value
        else:
            return self.succ.store(value)

    def lookup(self, key: int):

        """
        Lookup the value of a key.
        :param key:
        :return:
        """
        if clock_dist(self.id, key) > clock_dist(self.succ.id, key):
            # Forward going closer to responsible node
            return f"{key}:{self}# -> " + self.succ.lookup(key)
        else:
            if key in self.storage.keys():
                return f"{key}:{self}H -> " + self.storage[key]
            else:
                return f"{key}:{self}ø "

    def lkwrp(self, key: int, original_caller: 'NodeDHT'):
        if clock_dist(self.id, key) > clock_dist(self.succ.id, key):
            return f"-> {self}# " + self.succ.lkwrp(key, original_caller)
        elif key in self.storage.keys():
            return f"-> {self}@ " + self.storage[key]
        else:
            return f"-> {self} ø"

    def print_storage(self):
        print(f"{self}")
        print("---------------")
        for key, value in sorted(self.storage.items()):
            print(f"{key} -> {value}")
        print("---------------")
        print("\n")

    def __str__(self):
        return f"{str(self.name)}@{str(self.id)}"

    def __lt__(self, other):
        return self.id < other.id


def print_ring(start_node: 'NodeDHT'):
    """
    Print the ring.
    """
    start = start_node.succ
    while start != start_node:
        print(f"{start} ->", end=" ")
        start = start.succ
    print(start)


def main():
    """
    Main function.
    """
    # print(compute_key('hello'))
    # print(compute_key('world'))
    # print(clock_dist(compute_key('hello'), compute_key('world')))
    # for i in range(100):
    #     print(clock_dist(1, 4, 12))
    #     print(clock_dist(11, 1, 12))

    n1 = NodeDHT('n1')
    n2 = NodeDHT('n2')

    n1.set_successor(n2)
    n1.set_predecessor(n2)

    n2.set_successor(n1)
    n2.set_predecessor(n1)

    print("Creating more nodes that join existing ones!")
    n3 = NodeDHT('n3')
    n4 = NodeDHT('n4')

    n2.join(n3)
    n1.join(n4)

    print_ring(n1)

    divina = "cammin Nel mezzo del cammin di nostra vita " \
             "mi ritrovai per una selva oscura, " \
             "che la diritta via era smarrita. " \
             "Ahi quanto a dir qual era è cosa dura " \
             "esta selva selvaggia e aspra e forte " \
             "che nel pensier rinova la paura!   "

    divina_keywords = list(dict.fromkeys(
        divina.lower()
            .replace(",", " ")
            .replace(";", " ")
            .replace(".", " ")
            .replace("!", " ")
            .split())
    )

    # print(divina_keywords)

    for keyword in divina_keywords:
        n1.store(keyword)

    nodes = [n1, n2, n3, n4]
    for node in sorted(nodes):
        node.print_storage()

    for keyword in divina_keywords:
        key = compute_key(keyword)
        print(n1.lookup(key))

    print(n1.lookup(compute_key('uffa')))


if __name__ == '__main__':
    main()
