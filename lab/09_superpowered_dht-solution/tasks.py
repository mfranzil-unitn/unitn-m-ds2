from invoke import task
from dht.util import Process
from subprocess import Popen
from time import sleep


IP = 'localhost'

def startProcess(port, name, predDesc = None, succDesc = None):
    args = ['python', 'runserver.py', '-n', name, '-k', IP, '-p', port]
    desc = "_".join([IP, str(port), name])

    if predDesc:
        args += ['-v', predDesc]

    if succDesc:
        args += ['-s', succDesc]

    outfile = open('logs/{}.log'.format(desc), 'w')
    errfile = open('logs/{}-err.log'.format(desc), 'w')

    print(" ".join(args))
    p = Popen(args, stdout = outfile, stderr = errfile)

    sleep(1)



@task
def boot(ctx):
    print("Booting a network with 2 hardwired nodes")

    p1 = Process(IP, '10001', 'PROC10001')
    p2 = Process(IP, '10002', 'PROC10002')

    startProcess(p1.port, p1.name, p2.hostportname(), p2.hostportname())
    startProcess(p2.port, p2.name, p1.hostportname(), p1.hostportname())

@task
def killall(ctx):
    ctx.run('pkill -9 -f runserver.py', warn=True, echo=True)


@task(killall, boot)
def reboot(ctx):
    print("REBOOT COMPLETED!")