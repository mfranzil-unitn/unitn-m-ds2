from threading import Thread
from uuid import uuid4
from random import randint
from datetime import datetime as dt
from time import sleep
import json
from hashlib import sha256, md5
from numpy.random import exponential


def compute_proof(block):
    block_string = json.dumps(block, sort_keys=True)
    proof = sha256(block_string.encode()).hexdigest()
    return proof


def nonce(now):
    return sha256(now.encode()).hexdigest()[:16]


def genesisBlock():
    block = {
        'index': 0,
        'timestamp': dt(1970, 1, 1).isoformat(),
        'blockhash': 'NAKAMOTO'
    }
    return block


def block_summary(block):
    s = {k: v[:12] for k, v in block.items() if type(v) == str}
    s['transactions'] = ['...']
    retval = block.copy()
    retval.update(s)
    return dict(retval)
