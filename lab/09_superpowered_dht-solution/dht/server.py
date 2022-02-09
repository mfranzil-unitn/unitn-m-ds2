from flask import Flask, jsonify, request, abort
from .util import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def ping():
  """
  Returns when the server is ready.
  """
  return '{} is alive'.format(app.proc.name)

@app.route('/find/<int:key>', methods=['GET'])
def find(key):
  n, r = findNode(app.proc, key)
  return "Node responsible for key={} is {}".format(key, n.name)


@app.route('/nodeinfo', methods=['GET'])
def nodeinfo():
  return jsonify(app.proc.toJSON())


@app.route('/pred', methods=['GET', 'PUT'])
def predecessor():
  if request.method == 'GET':
    if not app.proc.pred:
      abort(404, "No predecessor found")
      return "No predecessor found"
    return jsonify(app.proc.pred.toJSON())

  elif request.method == 'PUT':
    data = request.data.decode('utf-8').split(':')
    newpred = Process(data[0], data[1], data[2])
    app.proc.pred = newpred
    return "New node info updated with newpred: \n{}".format(app.proc.pred.toJSON())


@app.route('/succ', methods=['GET', 'PUT'])
def successor():
  if request.method == 'GET':
    if not app.proc.succ:
      abort(404, "No successor found")
      return "No successor found"
    return jsonify(app.proc.succ.toJSON())

  elif request.method == 'PUT':
    data = request.data.decode('utf-8').split(':')
    newsucc = Process(data[0], data[1], data[2])
    app.proc.succ = newsucc
    return "New node info updated with newsucc: \n{}".format(app.proc.succ.toJSON())



@app.route('/db', methods=['GET'])
def keys():
  """
  Returns all keys stored on THIS node in plain text separated by a carriage
  return and a new line:

    <key1>\r\n<key2>\r\n...
  """
  raise NotImplemented

@app.route('/db/<key>', methods=['GET'])
def get(key):
  """
  Returns the value for the key stored in this DHT or an empty response
  if it doesn't exist.
  """
  return key

@app.route('/db/<key>', methods=['POST', 'PUT'])
def put(key):
  """
  Upserts the key into the DHT. The value is equal to the body of the HTTP
  request.
  """
  raise NotImplemented

@app.route('/db/<key>', methods=['DELETE'])
def delete(key):
  """
  Deletes the key from the DHT if it exists, noop otherwise.
  """
  raise NotImplemented

@app.route('/dht/peers', methods=['GET'])
def peers():
  """
  Returns the names of all peers that form this DHT in plain text separated by
  a carriage return and a new line:

    <peer1>\r\n<peer2>\r\n
  """
  raise NotImplemented

@app.route('/dht/join', methods=['POST'])
def join():
  data = request.json

  joinerID = data['id']

  info("{} is trying to welcome {}".format(app.proc.hostportname(), joinerID))

  joiner = Process(data['host'], data['port'], data['name'])  

  resp, recLevel = findNode(app.proc, joinerID)
  info("This is what we know about the responsible node:\n{}".format(resp.toJSON()))
  info("This is what we know about the joiner:\n{}".format(joiner.toJSON()))

  predOfResp = resp.pred

  info("This is what we know about the joiner:\n{}".format(predOfResp.toJSON()))

  predurl = "http://{}:{}/pred".format(joiner.host, joiner.port)
  succurl = "http://{}:{}/succ".format(joiner.host, joiner.port)

  requests.put(predurl, data=predOfResp.hostportname())
  requests.put(succurl, data=resp.hostportname())

  #STOP




@app.route('/dht/leave', methods=['GET'])
def leave():
  """
  Leave the current DHT. This request should only retrn the DHT this node
  is leaving has stabilized and this node is a standalone node now; noop is
  not part of any DHT.
  """
  raise NotImplemented

def start_app(host, port, name, pred=None, succ=None):
  app.proc : Process or None = Process(host, port, name, pred, succ)
  app.run(host=host, port=port)