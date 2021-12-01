from hashlib import sha256
from bitstring import BitArray
import sys
import logging
import requests

BITLENGTH = 32

logging.basicConfig(level = logging.INFO, stream = sys.stdout)
logger = logging.getLogger(__name__)

def info(string):
    #logger.info(string)
    print(string, flush = True)



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



'''def findNode(startnode, key):
    """Recursively find the node whose ID is the greatest
     but smaller ID in the DHT compared to key"""
    current = startnode
    recLevel = 0
    while dist(current.id, key) > dist(current.succ.id, key):
        current = current.succ
        recLevel += 1
    #print("current {}, succ {}, key {}".format(current.id, current.succ.id, key))
    return current, recLevel'''

def processFromNodeInfo(host, port):
    url = "http://{}:{}/nodeinfo".format(host, port)
    respJSON = requests.get(url).json()
    name, pred, succ = respJSON['name'], respJSON['pred'], respJSON['succ']
    return Process(host, port, name, pred, succ)

def findNode(startProcess, key):

    current = startProcess
    succ = processFromNodeInfo(startProcess.succ.host, startProcess.succ.port)
    recLevel = 0

    info("Entering the findNode routine")
    currentID, succID = current.id, succ.id

    while dist(currentID, key) > dist(succID, key):
        
        info("succ {} is closer to key {} than current {}".format(succID, key, currentID))
        
        currentID = succ.ID
        succ = processFromNodeInfo(succ.succ.host, succ.succ.port)
        succID = succ.id

        info("\t Now we retry with {} {}".format(succ.name, succID))
        recLevel += 1

    info("{} is the good one!!!".format(succ.hostportname()))
    return succ, recLevel
