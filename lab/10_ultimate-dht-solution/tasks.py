from invoke import task
from subprocess import Popen
from dht.util import compute_key, BITLENGTH, Process, wordsOfFile
import code  # code.interact(local=dict(globals(), **locals()))
import json
import random
import requests
from flask import Flask, current_app, request, jsonify, abort
import subprocess
import os
from time import sleep
from tabulate import tabulate

IP = 'localhost'
BASEPORT = 10001

processFile = 'processes.json'


def read_process_list():
    if not os.path.exists(processFile):
        return []
    with open(processFile, 'r') as f:
        return json.load(f)


def persist_process_list(processes):
    with open(processFile, 'w') as f:
        json.dump(processes, f)


def startProcess(port, name, predDesc=None, succDesc=None):
    desc = ":".join([IP, str(port), name])
    args = ['python', 'runserver.py', '-n', name, '-k', IP, '-p', port]

    if predDesc:
        args += ['-v', predDesc]

    if succDesc:
        args += ['-s', succDesc]

    outfile = open('logs/{}.log'.format(desc), 'w')
    errfile = open('logs/{}-err.log'.format(desc), 'w')
    print('Starting node: {}'.format(desc))

    print(" ".join(args))
    p = Popen(args, stdout=outfile, stderr=errfile)

    processes = read_process_list()
    persist_process_list(processes + [desc])
    sleep(1)


def pick_random_process():
    processes = read_process_list()
    desc = random.choice(processes)
    ip, port, name = desc.split(':')
    return Process(ip, port, name)


@task()
def boot(ctx):
    """Start up local DHT with 2 hardwired nodes"""
    if os.path.exists(processFile):
        os.remove(processFile)

    print("Booting a DHT with 2 intial hardwired process")

    p1 = Process(IP, '10001', 'PROC10001')
    p2 = Process(IP, '10002', 'PROC10002')

    startProcess(p1.port, p1.name, p2.hostportname(), p2.hostportname())
    startProcess(p2.port, p2.name, p1.hostportname(), p1.hostportname())



@task
def killall(ctx):
    ctx.run('pkill -9 -f runserver.py', warn=True, echo=True)
    if os.path.exists(processFile):
        os.remove(processFile)


@task(killall, boot)
def reboot(ctx):
    print("Rebooted successfully!")


@task
def add(ctx, rndproxy=False):
    """Add a random node to the cluster to test JOIN"""
    processes = read_process_list()

    ip, port, name = 'localhost', '10001', 'PROC10001'
    if rndproxy:
        rndp = pick_random_process()
        ip, port, name = rndp.hostportname().split(':')
        #ip, port, name = random.choice(processes).split(":")

    newport = str(BASEPORT + len(processes))
    newname = "PROC{}".format(newport)
    newdesc = ":".join([IP, newport, newname])

    startProcess(str(newport), newname)

    print("Node {} asks to join from {}".format(newname, name))
    joinerProcess = Process(IP, newport, newname)

    joinerJSON = joinerProcess.toJSON()
    url = "http://{}:{}/dht/join".format(ip, port)
    print(url)
    r = requests.post(url, json=joinerJSON)
    print("  ", r.status_code)


@task
def addmany(ctx, howmany):
    """Add a random node to the cluster to test JOIN"""
    processes = read_process_list()

    for i in range(int(howmany)):
        print("Adding {} out of {}".format(i+1, howmany))
        add(ctx, rndproxy=True)


@task
def lookup(ctx, value):
    key = compute_key(value)
    print("Looking up for key = {} --> value = {}".format(key, value))

    rndp = pick_random_process()
    ip, port, name = rndp.hostportname().split(':')

    url = "http://{}:{}/lookup/{}".format(ip, port, key)
    print(url)
    r = requests.get(url)
    print("  ", r.status_code)
    print(r.json())
    sleep(0.1)


@task
def store(ctx, value):
    print("Storing {}...".format(value))

    rndp = pick_random_process()
    ip, port, name = rndp.hostportname().split(':')

    url = "http://{}:{}/store/{}".format(ip, port, value)
    print(url)
    r = requests.get(url)
    print("  ", r.status_code)
    sleep(0.1)


@task
def storemany(ctx, howmany):
    """Add a random node to the cluster to test JOIN"""
    moreWords = wordsOfFile("lipsum.txt")

    for i in range(int(howmany)):
        value = random.choice(moreWords)
        print("#{}/{} -> STORE {} somewhere...".format(i+1, howmany, value))
        store(ctx, value)


@task
def monitor(ctx):
    processes = read_process_list()

    node2content = {}
    for proc in processes:
        ip, port, name = proc.split(':')
        url = "http://{}:{}/db".format(ip, port)
        ht = requests.get(url).json()

        s = "{}\n{}".format(name, compute_key(name))
        node2content[compute_key(name)] = list(sorted(ht.items()))
    srtd = dict(sorted(node2content.items()))
    print(tabulate(srtd, headers='keys', tablefmt='pretty'))
