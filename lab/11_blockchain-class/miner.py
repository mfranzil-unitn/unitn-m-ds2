from util import *
import paho.mqtt.client as mqtt


TRXGENERATIONINTERVAL = 5
mqttBroker = 'localhost'


def mine(miner):
    while True:
        # keep mining!
        pass


def genTRX(miner, INTERVAL):
    while True:
        trx = {'sender': miner.name, 'timestamp': dt.now().isoformat()}
        miner.publishTRX(trx)
        sleep(exponential(INTERVAL))


class Miner():

    def __init__(self, host, port):
        uid = str(uuid4()).replace('-', '')
        self.host = host
        self.port = port
        self.name = f'MINER-{port}'
        self.id = uid

        self.blockchain = [genesisBlock()]
        self.trxs = []  # list of pending TRXs

        self.blockProducer = mqtt.Client(f'{uid}BlockProducer')
        self.TrxProducer = mqtt.Client(f'{uid}TrxProducer')
        self.blockConsumer = mqtt.Client(f'{uid}BlockConsumer')
        self.TrxConsumer = mqtt.Client(f'{uid}TrxConsumer')

        self.initMQTT()

        self.mining = Thread(target=mine, args=(self,), daemon=True)
        self.TRXgeneration = Thread(target=genTRX, args=(
            self, TRXGENERATIONINTERVAL), daemon=True)

    def initMQTT(self):
        self.blockProducer.connect(mqttBroker)
        self.TrxProducer.connect(mqttBroker)
        self.blockConsumer.connect(mqttBroker)
        self.TrxConsumer.connect(mqttBroker)

        self.blockConsumer.subscribe("NEWBLOCK")
        self.TrxConsumer.subscribe("NEWTRX")

        self.blockConsumer.on_message = self.on_newblock
        self.TrxConsumer.on_message = self.on_newtrx

    def on_newblock(self, client, userdata, message):
        pass

    def on_newtrx(self, client, userdata, message):
        decoded = str(message.payload.decode('utf-8'))
        trx = json.loads(decoded)
        if trx['sender'] != self.name:
            print(f"{self.name} RECEIVED TRX  from {trx['sender']}")

    def addPendingTRX(self, trx):
        if trx not in self.trxs:
            self.trxs.append(trx)


    def publishTRX(self, trx):
        self.addPendingTRX(trx)
        print(f"{self.name}: generated TRX: {trx}")
        self.TrxProducer.publish("NEWTRX", json.dumps(trx, sort_keys=True))


    def publishBLOCK(self, trx):
        pass

    def start(self):
        print(f'Booting {self.name}')
        # let's start listening to new TRXs and BLOCKs
        self.blockConsumer.loop_start()
        self.TrxConsumer.loop_start()

        # thread start
        self.TRXgeneration.start()

        while True:
            #Wait for CTRL-C
            pass

    def stop(self):
        #Dump blockchain
        pass
