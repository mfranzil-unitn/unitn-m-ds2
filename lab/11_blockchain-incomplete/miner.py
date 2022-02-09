import json

import paho.mqtt.client as mqtt

from util import *

TRX_GEN_INTERVAL = 5
MQTTBROKER = 'localhost'
LEADING_ZEROS = 2


def block_summary(block):
    """
    Return a summary of a block
    """
    return f"{block['blockhash']} {block['timestamp']} {block['proof']}"


def mine(miner: 'Miner'):
    """
    Mine a new block
    """
    while True:
        block = miner.working_block()
        proof = compute_proof(block)
        if proof.startswith('0' * LEADING_ZEROS):
            block_string = json.dumps(block, sort_keys=True)
            bh = sha256(block_string.encode('utf-8')).hexdigest()
            block['blockash'] = bh
            print(f"\n{miner.name} mined this block: {block_summary(block)}")
            miner.publish_block(block)
            sleep(1)
        else:
            print(f"\n{miner.name} failed to mine a block: {proof}", end='\r')


def gentrx(miner: 'Miner', interval=TRX_GEN_INTERVAL):
    """
    Generate a new transaction
    """
    while True:
        trx = {
            'sender': miner.name,
            'timestamp': dt.now().isoformat()
        }
        miner.publish_trx(trx)
        sleep(exponential(interval))


class Miner:
    def __init__(self, host, port):
        uid = str(uuid4()).replace('-', '')
        self.name = f'MINER-{port}'
        self.host: str = host
        self.port: str = port
        self.id: str = uid

        self.blockchain: [] = [genesis_block()]
        self.trxs: [] = []  # List of pending transactions

        self.block_producer: mqtt.Client = mqtt.Client(f'{uid}BlockProducer')
        self.trx_producer: mqtt.Client = mqtt.Client(f'{uid}TrxProducer')
        self.block_consumer: mqtt.Client = mqtt.Client(f'{uid}BlockConsumer')
        self.trx_consumer: mqtt.Client = mqtt.Client(f'{uid}TrxConsumer')

        self.init_mqtt()
        self.mining: Thread = Thread(target=mine, args=(self,), daemon=True)
        self.trx_generation: Thread = Thread(target=gentrx, args=(self, TRX_GEN_INTERVAL), daemon=True)

    def init_mqtt(self):
        self.block_producer.connect(MQTTBROKER)
        self.trx_producer.connect(MQTTBROKER)
        self.block_consumer.connect(MQTTBROKER)
        self.trx_consumer.connect(MQTTBROKER)

        self.block_consumer.subscribe(f'NEWBLOCK')
        self.trx_consumer.subscribe(f'NEWTRX')

        self.block_consumer.on_message = self.on_newblock
        self.trx_consumer.on_message = self.on_newtrx

    def on_newblock(self, client, userdata, msg):
        decoded = str(msg.payload.decode('utf-8'))
        announcement = json.loads(decoded)
        if announcement['publisher'] != self.id:
            block = announcement['block']
            print(f"{self.name} received new block {block}")


    def on_newtrx(self, client, userdata, msg):
        decoded: str = str(msg.payload.decode('utf-8'))
        trx: {} = json.loads(decoded)

        if trx['sender'] != self.id:
            print(f"{self.name} received new transaction {trx}")

    def add_pending_trx(self, trx):
        if trx not in self.trxs:
            self.trxs.append(trx)

    def publish_trx(self, trx):
        self.add_pending_trx(trx)
        self.trx_producer.publish(f'NEWTRX', json.dumps(trx, sort_keys=True))
        print(f"{self.name} published new transaction {trx}")

    def publish_block(self, block):
        self.block_producer.publish(f'NEWBLOCK', json.dumps(block, sort_keys=True))
        print(f"{self.name} published new block {block}")

    def start(self):
        # Start listening to new transactions and blocks
        self.block_consumer.loop_start()
        self.trx_consumer.loop_start()

        self.trx_generation.start()

        while True:
            pass

    def stop(self):
        # Dump the blockchain
        self.block_consumer.loop_stop()
        self.trx_consumer.loop_stop()


    def working_block(self):
        now = dt.now().isoformat()
        reward = {
            'sender': self.id,
            'timestamp': now
        }

        block = {
            'index': len(self.blockchain) + 1,
            'timestamp': now,
            'transactions': self.trxs + [reward],
            'nonce': nonce(now),
            'previous_hash': self.blockchain[-1]['blockhash']
        }

        return block
