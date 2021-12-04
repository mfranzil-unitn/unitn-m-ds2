from flask import Flask, current_app, request, jsonify, abort, Response
import requests
import code  # code.interact(local=dict(globals(), **locals()))
from .util import *

app = Flask(__name__)


@app.route('/', methods=['GET'])
def ping():
    return "{} is alive".format(app.proc.name)


@app.route('/find/<int:key>', methods=['GET'])
def find(key):
    n, r = findNode(app.proc, key)
    return 'Node responsible for key={} is {}'.format(key, n.name)


@app.route('/db', methods=['GET'])
def showNodeContent():
    if not app.proc.ht:
        # just for debugging we return a dummy dict
        return jsonify({"NoContent": "empty_dict"})
    #retval = tabulate(app.proc.ht.items(), headers=['Key', 'Value'], tablefmt='html')
    return jsonify(app.proc.ht)


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
        return "New node info with updated pred: \n{}".format(app.proc.toJSON())


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
        return "New node info with updated succ: \n{}".format(app.proc.toJSON())


@app.route('/dht/join', methods=['POST'])
def join():
    """
    data received = {"joinerID": <int>}
    1) findNode
    2) Rewiring
    3) Rebalancing Content
    """
    data = request.json
    joinerID = data['id']
    print("{} is trying to let {} join in".format(
        app.proc.hostportname(), joinerID))

    info("This is what we know about joiner: {}\n".format(request.json))
    joiner = Process(data['host'], data['port'], data['name'])

    resp, recLevel = findNode(app.proc, joinerID)
    info("This is what we know about responsible: {}".format(resp.toJSON()))
    predOfResp = resp.pred
    info("This is what we know about current Pred Of Resp: {}".format(
        predOfResp.toJSON()))

    '''Rewiring...
    1) pred and succ of JOINER should be, respectively, predOfResp and resp itself
    2) JOINER becomes, respectively, the successor of predOfResp & the predecessor of resp
    '''

    predurl = "http://{}:{}/pred".format(joiner.host, joiner.port)
    succurl = "http://{}:{}/succ".format(joiner.host, joiner.port)

    requests.put(predurl, data=predOfResp.hostportname())
    requests.put(succurl, data=resp.hostportname())

    # check not sending a PUT request to ourself!!!
    if predOfResp.hostport() != app.proc.hostport():
        succurl = "http://{}:{}/succ".format(predOfResp.host, predOfResp.port)
        requests.put(succurl, data=joiner.hostportname())
    else:
        # we can manually update our succ
        app.proc.succ = joiner

    if resp.hostport() != app.proc.hostport():
        predurl = "http://{}:{}/pred".format(resp.host, resp.port)
        requests.put(predurl, data=joiner.hostportname())
    else:
        # we can manually update our pred
        app.proc.pred = joiner

    return "{} guided the JOIN procedure of {} which is now in the DHT".format(app.proc.hostportname(), joinerID)


@app.route('/insert', methods=['POST'])
def insert():
    data = request.json
    key, value = int(data['key']), data['value']
    app.proc.ht[key] = value
    return Response(status=200)


@app.route('/store/<value>', methods=['GET'])
def store(value):
    key = compute_key(value)
    resp, recLevel = findNode(app.proc, key)

    # Sending data to responsible node
    url = "http://{}:{}/insert".format(resp.host, resp.port)
    requests.post(url, json={"key": key, "value": value})

    return "<{}:{}> inserted on node {}".format(key, value, resp.hostportname())


@app.route('/get/<int:key>', methods=['GET'])
def get(key):
    retval = {'nodeResponsible': app.proc.hostportname()}
    try:
        value = app.proc.ht[key]
        retval.update({'result': value})
    except KeyError:
        retval.update({'result': None})

    return jsonify(retval)


@app.route('/lookup/<key>', methods=['GET'])
def lookup(key):
    key = int(key)
    info("{} is looking for requested key: {}".format(
        app.proc.hostportname(), key))
    resp, recLevel = findNode(app.proc, key)

    # Asking to responsible node
    url = "http://{}:{}/get/{}".format(resp.host, resp.port, key)
    respJSON = requests.get(url).json()

    info("We found requested data: {} at node: {}".format(
        respJSON, resp.hostportname()))
    return respJSON


@app.route('/db/<key>', methods=['DELETE'])
def delete(key):
    """
    Deletes the key from the DHT if it exists, noop otherwise.
    """
    raise NotImplemented


@app.route('/dht/leave', methods=['GET'])
def leave():
    """
    Leave the current DHT. This request should only retrn the DHT this node
    is leaving has stabilized and this node is a standalone node now; noop is
    not part of any DHT.
    """
    raise NotImplemented


def start_app(host, port, name, pred=None, succ=None):
    app.proc = Process(host, port, name, pred, succ)
    app.run(host=host, port=port)
