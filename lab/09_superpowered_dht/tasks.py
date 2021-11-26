from subprocess import Popen
from time import sleep

from invoke import task

from dht.util import Process

IP = 'localhost'


@task(default=True)
def boot(ctx):
    print("Booting a network with two hard-wired nodes...")
    p1 = Process(IP, '10001', 'PROC10001')
    p2 = Process(IP, '10002', 'PROC10002')

    startProcess(p1.port, p1.name, p2.hostportname(), p2.hostportname())
    startProcess(p2.port, p2.name, p1.hostportname(), p1.hostportname())


@task()
def killall(ctx):
    ctx.run('pkill -9 -f runserver.py', warn=True, echo=True)


@task(killall, boot)
def reboot(ctx):
    print("Rebooted the network.")


def startProcess(port, name, pred_desc, succ_desc) -> Popen:
    args = ['python3', 'runserver.py', '--port', port, '--name', name, '--host', IP]

    desc = "_".join([IP, str(port), name])
    if pred_desc:
        args.extend(['--pred', pred_desc])

    if succ_desc:
        args.extend(['--succ', succ_desc])

    outfile = open(f'logs/{desc}.log', 'w')
    #errfile = open(f'logs/{desc}.err', 'w')

    print(" ".join(args))
    p = Popen(args, stdout=outfile)#, stderr=errfile)

    sleep(1)

    return p