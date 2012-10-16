from socket import create_connection
from line import Line, DebugLine
from piv import Piv, Kshd
from sys import argv
from getopt import getopt
from time import sleep
from datetime import datetime, timedelta

channel = 0
address = 1
hostname = "beam-daq"
port = 10002
speed = 100

def printHelp():
    print("""
Sets current output value for Adam4024
testAdam4024 [-h] [-s hostname:port] 
-h               - show help
-s hostname:port - connect to this tcp port (default: %s:%d)
-a number        - an address in PIV protocol (default:1)
-r speed
""" % (hostname, port))


opts, args=getopt(argv[1:], "hs:a:r:")
for key, value in opts:
    if key == "-a":
        address = int(value)
    if key == "-s":
        pair = value.split(":")
        hostname = pair[0]
        port = int(pair[1])
    if key == "-h":
        printHelp()
        exit(1)
    if key == "-r":
        speed = int(value)

socket = create_connection((hostname, port))
line = Line(socket)
#line = DebugLine(line)

piv = Piv(line)
kshd = Kshd(piv, address)
kshd.stop()
if True:
    kshd.setCoordinate(0)
    conf = kshd.getConfiguration()
    conf.moveCurrent = 1
    conf.holdDelay = 0.5
    kshd.setConfiguration(conf)
print(kshd.getConfiguration())
print(kshd.getSpeed())

def wait():
    while True:
        s = kshd.status()
#        print(s)
        #print("To go:",kshd.getStepsToGo())
        if s.ready:
            print("Coordinate", kshd.getCoordinate())
            break
    
wait()
def benchmark(f):
    start = datetime.now()
    f()
    stop = datetime.now()
    print((stop-start).total_seconds())

def run(speed):
    def r():
        speedConf = kshd.getSpeed()
        speedConf.max = speed
        kshd.setSpeed(speedConf)
        print(kshd.getSpeed())
        kshd.go(4000)
        wait()
    return r
#benchmark(run(1000))
#benchmark(run(5000))
#benchmark(run(10000))
#benchmark(run(6000))
try:
    run(speed)()
except:
    kshd.stop()
    raise
    



