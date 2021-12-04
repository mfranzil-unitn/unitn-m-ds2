from hashlib import sha256
from bitstring import BitArray
import sys
import logging
import requests

BITLENGTH = 32

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def info(string):
    # logger.info(string)
    print(string, flush=True)


def compute_key(string, bitlength=BITLENGTH):
    digest = sha256(bytes(string, 'utf-8')).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    return BitArray(bin=subbin).uint


def dist(a, b, maxnum=2 ** BITLENGTH - 1):
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

        self.ht = {}
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

    def hostportname(self):
        return "{}:{}:{}".format(self.host, self.port, self.name)


def processFromNodeInfo(host, port):
    url = f"http://{host}:{port}/nodeinfo"
    respJSON = requests.get(url).json()
    name, pred, succ = respJSON['name'], respJSON['pred'], respJSON['succ']
    return Process(host, port, name, pred, succ)


def find_node(startProcess, key):
    current = startProcess
    succ = processFromNodeInfo(startProcess.succ.host, startProcess.succ.port)
    recLevel = 0

    info("Entering the findNode routine")
    currentID, succID = current.id, succ.id

    while dist(currentID, key) > dist(succID, key):
        info(f"succ {succID} is closer to key {key} than current {currentID}")
        currentID = succ.id
        succ = processFromNodeInfo(succ.succ.host, succ.succ.port)
        succID = succ.id

        info(f"\t Now we retry with {succ.name} {succID}")
        recLevel += 1

    info(f"{succ.hostportname()} is the good one!!!")
    return succ, recLevel


def words_of_file(file):
    words = []
    with open(file, 'r') as file:
        for line in file:
            for word in line.split():
                words.append(word)
    return words
