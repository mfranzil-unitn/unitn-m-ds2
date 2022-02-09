from flask import Flask, request, abort

from process import Process
import logging as log

app = Flask(__name__)
app.proc = None


#@app.before_first_request
def start_node(host, port, name, pred=None, succ=None):
    """
    Start the DHT.
    """
    app.proc = Process(host, port, name, pred, succ)
    app.run(host=host, port=port, debug=True)

    return f"{host}:{port}:{name}"


@app.route('/', methods=['GET'])
def ping():
    """
    Returns when the server is ready.
    """
    if app.proc is not None:
        return 'pong', 200
    else:
        return '', 500


@app.route('/nodeinfo', methods=['GET'])
def nodeinfo():
    """
    Returns a JSON representation of the node
    :return: a JSON object
    """
    if app.proc is not None:
        return str(app.proc), 200
    else:
        return '', 500


@app.route('/pred', methods=['GET'])
def pred():
    """
    Returns the name of the predecessor of this node in [name:host:port] format.
    """
    if app.proc is not None:
        if app.proc.pred is not None:
            return str(app.proc.pred), 200
        else:
            #abort(404, 'This node has no predecessor')
            return {'status': 404, 'exception': 'This node has no predecessor'}, 404
    else:
        return '', 500


@app.route('/pred', methods=['POST', 'PUT'])
def set_pred():
    """
    Set the predecessor of this node.
    """
    if app.proc is not None:
        data = request.json.pred.split(':')
        pred = Process(data[0], data[1], data[2])
        app.proc.pred = pred
        return '', 200
    else:
        return '', 500


@app.route('/succ', methods=['GET'])
def succ():
    """
    Returns the name of the successor of this node in [name:host:port] format.
    """
    if app.proc is not None:
        if app.proc.succ is not None:
            return str(app.proc.succ), 200
        else:
            abort(404, 'This node has no successor')
            return {'status': 404, 'exception': 'This node has no successor'}, 404
    else:
        return '', 500


@app.route('/succ', methods=['POST', 'PUT'])
def set_succ():
    """
    Set the successor of this node.
    """
    if app.proc is not None:
        data = request.json.succ.split(':')
        succ = Process(data[0], data[1], data[2])
        app.proc.succ = succ
        return 'Node successor set: {succ}', 200
    else:
        return '', 500


# """"""""""""""""""""""""""""""
# """"""""""""""""""""""""""""""
# """"""""""""""""""""""""""""""
# """"""""""""""""""""""""""""""


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


@app.route('/dht/join', methods=['POST', 'PUT'])
def join():
    """
    Join a new DHT. If this node is already a member of a DHT, leave that
    DHT cooperatively. At least one node of the DHT that we are joining will
    be present in the request body.

    HTTP request body will look like:

      <name1>:<host1>:<port1>\r\n<name2>:<host2>:<port2>...
    """
    raise NotImplemented


@app.route('/dht/leave', methods=['GET'])
def leave():
    """
    Leave the current DHT. This request should only retrn the DHT this node
    is leaving has stabilized and this node is a standalone node now; noop if
    not part of any DHT.
    """
    raise NotImplemented
