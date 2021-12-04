from asyncio import sleep

import requests
from invoke import task


@task
def run(c):
    node0 = ('localhost', '8000', 'node0')
    node1 = ('localhost', '8001', 'node1')

    res0 = c.run(f"python3 runserver.py --name {node0[2]} --port {node0[1]}", asynchronous=True)
    res1 = c.run(f"python3 runserver.py --name {node1[2]} --port {node1[1]}", asynchronous=True)

    sleep(10)

    requests.put(f"http://{node0[0]}:{node0[1]}/" + 'succ', data={'succ': ":".join(node1)})
    requests.put(f"http://{node1[0]}:{node1[1]}/" + 'pred', data={'pred': ":".join(node0)})
