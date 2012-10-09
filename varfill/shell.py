#!/usr/bin/python3 -i
from socket import create_connection
from line import Line
from adam import Adam4024
from sys import argv
from getopt import getopt
from time import sleep
from piv import Kshd, Piv

channel = 3
address = 1
hostname = "beam-daq"
port = 10002

def printHelp():
    print("""
Sets current output value for Adam4024
testAdam4024 [-h] [-s hostname:port] channel value 
-h               - show help
-s hostname:port - connect to this tcp port (default: %s:%d)
""" % (hostname, port))


opts, args=getopt(argv[1:], "hs:")
for key, value in opts:
    if key == "-s":
        pair = value.split(":")
        hostname = pair[0]
        port = int(pair[1])
    if key == "-h":
        printHelp()
        exit(1)

socket = create_connection((hostname, port))
line = Line(socket)
dac = Adam4024(line, address)
for ch in range(4):
    dac.setChannel(ch, 0)    
dac.setChannelOutputRange(channel, 1)

piv = Piv(line)
kshd = Kshd(piv, 1)
