from hashlib import sha256
from bitstring import BitArray

BITLENGTH = 32


def compute_key(string, bitlength=BITLENGTH):
    digest = sha256(bytes(string, 'utf-8')).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    return BitArray(bin=subbin).uint


def dist(a, b, maxnum=2**BITLENGTH - 1):
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)

class Process():
    
    def __init__(self, host, port, name, pred=None, succ=None):
        self.name = name
        self.id = compute_key(name)
        self.host = host
        self.port = port

        if pred:
            phost, pport, pname = pred.split(":")
            self.pred = Process(phost, pport, pname)
        else:
            self.pred = None

        if succ:
            phost, pport, pname = pred.split(":")
            self.succ = Process(phost, pport, pname)
        else:
            self.succ = None

        self.ht = dict()
        self.finger = dict()

    def toJSON(self):
        retval = {}
        retval['name'] = self.name
        retval['id'] = self.id
        retval['host'] = self.host
        retval['port'] = self.port

        if self.pred:
            retval['pred'] = self.pred.hostportname()
        else:
            retval['pred'] = None

        if self.succ:
            retval['succ'] = self.succ.hostportname()
        else:
            retval['succ'] = None

        return retval

    def hostportname(self):
        return "{}:{}:{}".format(self.host, self.port, self.name)

