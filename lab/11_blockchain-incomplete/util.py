import json
from hashlib import sha256
from uuid import uuid4
from datetime import datetime as dt
from time import sleep
from threading import Thread

from numpy.random import exponential

def compute_proof(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return sha256(block_string).hexdigest()

def nonce(now):
    """Generates a random nonce"""
    return sha256(str(now).encode()).hexdigest()[:16]

def genesis_block():
    """Creates the genesis block"""
    block = {
        'index': 0,
        'timestamp': dt(1970, 1, 1).isoformat(),
        'blockhash': 'NAKAMOTO',
    }

    return block

