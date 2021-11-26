import logging
import sys
from hashlib import sha256

import requests
from bitstring import BitArray

BITLENGTH = 32

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def info(string: str):
    # print(string, flush = True)
    logger.info(string)


def compute_key(string: str, bitlength: int = BITLENGTH):
    digest = sha256(bytes(string, 'utf-8')).hexdigest()
    bindigest = BitArray(hex=digest).bin
    subbin = bindigest[:bitlength]
    #info(f"{string}->{BitArray(bin=subbin).uint}")
    return BitArray(bin=subbin).uint


def dist(a: int, b: int, maxnum: int = 2 ** BITLENGTH - 1):
    if a == b:
        return 0
    elif a < b:
        return b - a
    else:
        return maxnum - (a - b)


class Process():
    def __init__(self, host: str, port: int, name: str, pred: 'Process' or None = None, succ: 'Process' or None = None):
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
        retval: {} = {'name': self.name, 'id': self.id, 'host': self.host, 'port': self.port}

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
        return f"{self.host}:{self.port}:{self.name}"


def processFromNodeInfo(host : str, port : int) -> Process:
    url = f"http://{host}:{port}/nodeinfo"
    respJSON : {} = requests.get(url).json()
    name : str = respJSON['name']
    pred : str = respJSON['pred']
    succ : str = respJSON['succ']

    return Process(host, port, name, pred, succ)


def find_node(startnode: Process, key: int) -> (Process, int):
    current = startnode
    succ =  processFromNodeInfo(current.host, current.port)

    recLevel = 0
    info("Entering the findNode routine")
    current_id, succ_id = current.id, succ.id

    while dist(current_id, key) > dist(succ_id, key):
        info(recLevel*"\t" + f"(s) {succ} closer to (k) {key} than (c) {current} rcl: {recLevel}")
        current_id = succ_id
        succ = processFromNodeInfo(succ.succ.host, succ.succ.port)
        succ_id = succ.id
        recLevel += 1
        info(f"Now we retry with {succ.name} {succ_id}")
    # print("current {}, succ {}, key {}".format(current.id, current.succ.id, key))
    info(f"Phew, we did it. {succ.hostportname()} is the good one!!!!")
    return current, recLevel
