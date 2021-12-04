from hashlib import sha256
from bitstring import BitArray
import requests
import sys
import logging


BITLENGTH = 128


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def info(string):
    print(string, flush=True)
    # logger.info(string)


def compute_key(string, bitlength=BITLENGTH):
    digest = sha256(bytes(string, 'utf-8')).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    return BitArray(bin=subbin).uint


def dist(a, b, maxnum=2**BITLENGTH - 1):
    """Compute the clockwise dist between a and b,
     given maxnum as max clock value"""
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
            phost, pport, pname = pred.split(':')
            self.pred = Process(phost, pport, pname)
        else:
            self.pred = None

        if succ:
            phost, pport, pname = succ.split(':')
            self.succ = Process(phost, pport, pname)
        else:
            self.succ = None

        self.ht = dict()
        self.finger = {}

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

    def hostport(self):
        return "{}:{}".format(self.host, self.port)

    def hostportname(self):
        return "{}:{}:{}".format(self.host, self.port, self.name)

    def hostportnameJSON(self):
        return {"host": self.host, "port": self.port, "name": self.name}


def processFromNodeInfo(host, port):
    url = "http://{}:{}/nodeinfo".format(host, port)
    respJSON = requests.get(url).json()
    name, pred, succ = respJSON['name'], respJSON['pred'], respJSON['succ']
    return Process(host, port, name, pred, succ)


def findNode(startProcess, key):
    """Recursively find the node whose ID is the greatest
     but smaller ID in the DHT compared to key"""

    # if no successor probably startNode is alone...debuggin server :)
    if not startProcess.succ:
        return startProcess, 0

    current = startProcess
    succ = processFromNodeInfo(startProcess.succ.host, startProcess.succ.port)
    recLevel = 0

    info("Entering FindNode method")
    currentID, succID = current.id, succ.id

    while dist(currentID, key) > dist(succID, key):
        info("succ ({}) is closer to key ({}) than current ({})".format(
            succID, key, currentID))

        currentID = succ.id
        succ = processFromNodeInfo(succ.succ.host, succ.succ.port)
        succID = succ.id

        info("\tNow we rety with {} {}".format(succ.name, succID))
        recLevel += 1

    info("{} {} {} is the good one!".format(succ.host, succ.port, succ.id))
    return succ, recLevel


def wordsOfFile(file):
    words = []
    with open(file, 'r') as file:
        for line in file:
            for word in line.split():
                words.append(word)
    return words
