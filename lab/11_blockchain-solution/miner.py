import paho.mqtt.client as mqtt
from sortedcontainers import SortedDict
from util import *

mqttBroker = "localhost"

TRXGENINTERVAL = 1
LEADING_ZEROS = 2


def mine(miner):
    while True:
        block = miner.workingBlock()
        proof = compute_proof(block)
        if (proof.startswith("0" * LEADING_ZEROS)):
            # WE MINED A BLOOOOCK!!!!
            block_string = json.dumps(block, sort_keys=True)
            bh = sha256(block_string.encode()).hexdigest()
            block['blockhash'] = bh
            print(f"\n{miner.name}: MINED this block:\n{block_summary(block)}")
            miner.publishBLOCK(block)
            sleep(1)
        else:
            print(f"Useless proof = {proof}", end="\r")
            sleep(0.1)


def genTRX(miner, INTERVAL=1):
    """ Fake generation of a TRX on avg every INTERVAL sec"""
    while True:
        #print("Gen new TRX")
        trx = {'sender': miner.id, 'timestamp': dt.now().isoformat()}
        miner.publishTRX(trx)
        sleep(exponential(INTERVAL))


class Miner():

    def __init__(self, host, port):
        uid = str(uuid4()).replace('-', '')
        self.id = uid
        self.host = host
        self.port = port
        self.name = f"MINER-{port}"
        self.blockchain = [genesisBlock()]
        self.trxs = []
        #self.app = Flask(__name__)
        self.blockClient = mqtt.Client(f"{uid}BlockClient")
        self.trxClient = mqtt.Client(f"{uid}TrxClient")
        self.initMQTT()

        self.mining = Thread(target=mine, args=(self,), daemon=True)
        self.TRXgeneration = Thread(target=genTRX, args=(
            self, TRXGENINTERVAL), daemon=True)

    def initMQTT(self):
        self.blockClient.connect(mqttBroker)
        self.trxClient.connect(mqttBroker)

        self.blockClient.subscribe("NEWBLOCK")
        self.blockClient.on_message = self.on_newblock

        self.trxClient.subscribe("NEWTRX")
        self.trxClient.on_message = self.on_newtrx

    def publishTRX(self, trx):
        self.addPendingTRX(trx)
        self.trxClient.publish("NEWTRX", json.dumps(trx, sort_keys=True))

    def publishBLOCK(self, block):
        self.settleMinedTRXS(block['transactions'])
        self.blockchain.append(block)
        block
        announcement = {'publisher': self.id, 'block': block}
        self.blockClient.publish(
            "NEWBLOCK", json.dumps(announcement, sort_keys=True))

    def on_newblock(self, client, userdata, message):
        decoded = str(message.payload.decode("utf-8"))
        announcement = json.loads(decoded)
        if announcement['publisher'] != self.id:
            block = announcement['block']
            print(f"{self.name}: RECEIVED NEW BLOCK:\n{block_summary(block)}")
            self.settleMinedTRXS(block['transactions'])
            self.blockchain.append(block)
        else:
            #print("just my block")
            pass

    def on_newtrx(self, client, userdata, message):
        decoded = str(message.payload.decode("utf-8"))
        trx = json.loads(decoded)
        # only if it's not our own trx
        if trx['sender'] != self.id:
            # print(f"{self.name} got a new TRX")
            self.addPendingTRX(trx)
            # print(f"Now I have {len(self.trxs)} pending TRXs")

    def addPendingTRX(self, trx):
        if trx not in self.trxs:
            self.trxs.append(trx)

    def settleMinedTRXS(self, confirmedTRXs):
        for trx in confirmedTRXs:
            if trx in self.trxs:
                self.trxs.remove(trx)

    def workingBlock(self):
        now = dt.now().isoformat()
        reward = {'sender': self.id, 'timestamp': now}
        block = {
            'index': len(self.blockchain) + 1,
            'timestamp': now,
            'transactions': self.trxs + [reward],
            'nonce': nonce(now),
            'previous_hash': self.blockchain[-1]['blockhash']
        }
        return SortedDict(block)

    def start(self):
        self.blockClient.loop_start()
        self.trxClient.loop_start()

        self.TRXgeneration.start()
        self.mining.start()

        while True:
            # just wait ctr-c eheh
            pass

    def stop(self):
        print(f"Dumping {self.name} BLOCKCHAIN at shutdown")
        with open(f"logs/{self.name}BC.json", 'w') as f:
            f.write(json.dumps(self.blockchain, indent=2, sort_keys=True))
