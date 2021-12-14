from hashlib import sha256

from bitstring import BitArray

BITLENGTH = 32


def compute_key(string, bitlength=BITLENGTH):
    """Compute an hash digest BITLENGHT long and returns its integer value

    Args:
        string (str): the input for the hash function
        bitlength (int, optional): The length in bits of the hash output

    Returns:
        int: The integer resulting from the interpretation of the hash digest
        as an unsigned int in little endian notation
    """
    digest = sha256(bytes(string, 'utf-8')).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    return BitArray(bin=subbin).uint


def dist(a, b, maxnum=2 ** BITLENGTH - 1):
    """Compute the clockwise dist between a and b,
     given maxnum as max clock value"""
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)


class Process():
    def __init__(self, host: str, port: int, name: str, pred: str = None, succ: str = None):
        self.host = host
        self.port = port
        self.name = name
        self.id = compute_key(name)
        if pred:
            phost, pport, pname = pred.split(':')
            self.pred = Process(phost, pport, pname)
        else:
            self.pred = None
        if succ:
            shost, sport, sname = succ.split(':')
            self.succ = Process(shost, sport, sname)
        else:
            self.succ = None

        self.ht = {}
        self.finger = {}

    def __str__(self):
        return str(self.json())

    def json(self):
        return {'host': self.host,
                'port': self.port,
                'name': self.name,
                'id': self.id,
                'pred': self.pred,
                'succ': self.succ}
