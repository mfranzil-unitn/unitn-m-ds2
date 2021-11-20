# LAB 08 DHT, from simulation to web-based real implementation!!!

## Outline


1. Explain solution of last lab
   --> *advanced DHT with JOIN/LEAVE protocol + FingerTable*

2. **StepByStep implementation of a web-based DHT with Flask**

------------------------------------------------------------
------------------------------------------------------------
------------------------------------------------------------

### STEPS 4 a WEB-BASED DHT IMPLEMENTATION

- Define a DHTnode web-API with Flask
- Write down a "bootloader" script responsible of deploying single nodes
        * HINT: start from https://github.com/pipelinedb/pipelinedht
        * HINT: define a Node/Process class

*"Installing an app attribute at boot..."*
In the nodeAPI file
```Python
def start_app(host, port, name, pred=None, succ=None):
        app.proc = Process(host, port, name, pred, succ)
        app.run(host=host, port=port)
```


In the bootloader
```Python
start_app(host=args.host, port=args.port, name=args.name, pred=args.pred, succ=args.succ)
```


**1st Checkpoint**


- Use the bootloader to deploy one node (bound to localhost on some given port)
- Test dummy responses using POSTMAN


```
   snap install postman
```
------------------------------------------------------------


- Implement "node-info" method, to get all information needed to contact one node
- Implement successor and predecessor GET/PUT methods


**2nd Checkpoint**


Test with POSTMAN the 3 queries work as expected


------------------------------------------------------------


- Define common tasks:
   * NETWORK BOOT --> Boots two nodes thanks to the bootloader, wire them together manually
   * NETWORK KILL --> (VERY!!) useful for debugging purposes... when you want to restart the network after bug-fixing :)


NB:
- biggest troubles come from checking outputs of multiple nodes.
- Output must necessarily be redirected to files (goodbye consoles)
- Popen inside tasks 4 redirecting output to logfiles
- Tweak Flask to redirect stdout to your file




**3rd Checkpoint**


Check that py-invoke is really able to boot two nodes which are pred and succ of each other;
Check that you can kill all your DHTnode processes (and clean consoles/output files) when you need to do so.


------------------------------------------------------------


- Implement findNode(key) local method


        I mean, a Flask application (which is a DHT node), when asked to serve a JOIN / STORE / LOOKUP request
        should be able to identify the node responsible for the key associated to the received request.


        We will use an **iterative routing** approach, i.e., the "initiator" personally contacts all the many nodes
        that may be involved in the "redirects-chain" which leads to the discovery of the searched (responsible) node


**GOOD TO KNOW**: How to send web-requests via python-code (not anymore only through POSTMAN)


https://docs.python-requests.org/en/latest/


For example, if we want to implement the "LINEAR" findNode, then we must keep finding info
of successor nodes, until we find the good one...


Snippet to:
1. send a request to a given url and then
2. parse the JSON response we get that contains, wishfully, all data we need to know


```Python
def processFromNodeInfo(host, port):
        url = "http://{}:{}/nodeinfo".format(host, port)
        respJSON = requests.get(url).json()
        name, pred, succ = respJSON['name'], respJSON['pred'], respJSON['succ']
        return Process(host, port, name, pred, succ)
```


**4th Checkpoint**


Boot a network, add manually a node that you control via console, hardwire manually nodes,
issue a findNode and check with debugger/many print statemens that it works as expected


------------------------------------------------------------


- Implement JOIN (only correct placement of joinerNode)
- add a task that creates a joiner node, joiner should then ask to some already deployed node
to join


```Python
joinerJSON = joinerProcess.toJSON()
requests.post("http://{}:{}/dht/join".format(proxyip, proxyport), json=joinerJSON)
```


At the end of JOIN you should make rewirings via... PUT requests :)


```Python
predurl = "http://{}:{}/pred".format(joiner.host, joiner.port)
succurl = "http://{}:{}/succ".format(joiner.host, joiner.port)


requests.put(predurl, data=predOfResp.hostportname())
requests.put(succurl, data=resp.hostportname())
```


------------------------------------------------------------


Go ahead on your own! :)


After all the above steps you should have become super-expert with all needed tools necessary
for going further and implement also STORE / LOOKUP methods


Then if you have time implement also JOIN/LEAVE content rebalancing and finger tables!