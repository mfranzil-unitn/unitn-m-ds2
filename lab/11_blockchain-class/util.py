from uuid import uuid4
from datetime import datetime as dt
from numpy.random import exponential
from time import sleep
from threading import Thread
import json


def genesisBlock():
    """Creates the genesis block"""
    block = {
        'index': 0,
        'timestamp': dt(1970, 1, 1).isoformat(),
        'blockhash': 'NAKAMOTO',
    }
    return block
