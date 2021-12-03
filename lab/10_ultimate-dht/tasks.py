import random

import requests
from invoke import task
from dht.util import Process, words_of_file
from subprocess import Popen
from time import sleep
import os
import json

IP, BASEPORT = 'localhost', 10001
processesFile = 'processes.json'


def read_process_list():
    if not os.path.exists(processesFile):
        return []
    with open(processesFile, 'r') as f:
        return json.load(f)


def persist_process_list(processes):
    with open(processesFile, 'w') as f:
        json.dump(processes, f)


def pick_random_process() -> Process:
    processes = read_process_list()
    desc = random.choice(processes)
    ip, port, name = desc.split(':')

    return Process(ip, port, name)


def start_process(port, name, pred_desc=None, succ_desc=None):
    args = ['python', 'runserver.py', '-n', name, '-k', IP, '-p', port]
    desc = ":".join([IP, str(port), name])

    if pred_desc:
        args += ['-v', pred_desc]

    if succ_desc:
        args += ['-s', succ_desc]

    outfile = open('logs/{}.log'.format(desc), 'w')
    errfile = open('logs/{}-err.log'.format(desc), 'w')

    print(" ".join(args))
    p = Popen(args, stdout=outfile, stderr=errfile)

    processes = read_process_list()
    persist_process_list(processes + [desc])

    sleep(1)


@task
def boot(ctx):
    print("Booting a network with 2 hardwired nodes")

    p1 = Process(IP, '10001', 'PROC10001')
    p2 = Process(IP, '10002', 'PROC10002')

    start_process(p1.port, p1.name, p2.hostportname(), p2.hostportname())
    start_process(p2.port, p2.name, p1.hostportname(), p1.hostportname())


@task
def killall(ctx):
    ctx.run('pkill -9 -f runserver.py', warn=True, echo=True)
    if os.path.exists(processesFile):
        os.remove(processesFile)


@task(killall, boot)
def reboot(ctx):
    print("REBOOT COMPLETED!")


@task
def add(ctx, rndproxy=False):
    processes = read_process_list()

    ip, port, name = IP, '10001', 'PROC10001'

    if rndproxy:
        rndp = pick_random_process()
        ip, port, name = rndp.hostportname().split(':')

    newport = str(BASEPORT + len(processes))
    newname = 'PROC' + newport

    start_process(newport, newname)
    joiner_process = Process(IP, newport, newname)
    print("Node {} asks to join from {}".format(joiner_process.hostportname(), name))

    url = "http://{}:{}/dht/join".format(ip, port)
    print(url)
    r = requests.post(url, json=joiner_process.toJSON())
    print(" ", r.status_code)

@task
def addmany(ctx, howmany):
    for i in range(howmany):
        print(f"Adding {i + 1} out of {howmany}")
        add(ctx, rndproxy=True)

@task
def store(ctx, value):
    rndp = pick_random_process()

    url = f"http://{rndp.host}:{rndp.port}/store/{value}"
    print(url)
    r = requests.get(url)
    print(" ", r.status_code)
    sleep(0.1)

@task
def storemany(ctx, howmany):
    more_words = words_of_file('lipsum.txt')
    for i in range(howmany):
        value = random.choice(list(more_words))
        print(f"Storing {i + 1} out of {howmany} -> STORE {value} somewhere")
        store(ctx, value)