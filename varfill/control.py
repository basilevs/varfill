from socket import create_connection
from line import Line
from adam import Adam4024
from sys import argv
from getopt import getopt
from time import sleep
from piv import Kshd, Piv
from datetime import datetime, timedelta

class Mover(object):
    def setSpeed(self, speed):
        raise NotImplementedError
    def start(self):
        raise NotImplementedError
    def stop(self):
        raise NotImplementedError
    
class KshdMover(Mover):
    def __init__(self, kshd):
        assert(isinstance(kshd,Kshd))
        self.__kshd__ = kshd
    def setSpeed(self, speed):
        s = self.__kshd__.getSpeed()
        s.max = speed
        self.__kshd__.setSpeed(s)
    def start(self, speed):
        self.__kshd__.go(10000000)
    def stop(self):
        self.__kshd__.stop()

class Control(object):
    def __init__(self):
        self.pumps=[]
        self.mover=Mover()
        @staticmethod
        def dummy(seconds, pumpValues):
            pass
        self.stepCallback=dummy
        self.stopRequest = False
    def __stop__(self):
        self.stopRequest = True
        for i in range(len(self.pumps)):
            self.pumps[i](0)
        self.mover.stop()
    def executeProgram(self, time, moveSpeed, calcPumpValues):
        """ time - a total execution time in seconds
            moveSpeed - a speed of motor (will be constant during whole process)
            calPumpValues - a callable that should accept time in seconds since program start (floating point number)
            and return a tuple of pump speeds each speed should be a floating point in [0..1] 
        """           
        self.stopRequest = False
        self.mover.setSpeed(moveSpeed)
        start = datetime.now()
        until = start + timedelta(seconds = time)
        self.mover.start()
        while datetime.now() < until:
            if self.stopRequest:
                break
            seconds = (datetime.now() - start).total_seconds();
            values = calcPumpValues()
            for i in range(len(self.pumps)):
                self.pumps[i](values[i])
            self.stepCallback(seconds, values)
        self.__stop__()
    def stop(self):
        self.__stop__()
        
def defaultControl():
    s = create_connection(("beam-daq", 10002))
    line = Line(s)
    piv = Piv(line)
    kshd = Kshd(piv, 1)
    control = Control()
    control.mover = KshdMover(kshd)
    adam1 = Adam4024(line, 1)
    adam1.setChannelOutputRange(3, 1)
    def pump1(value):
        adam1.setChannel(3, value*20+4)
    control.pumps = [pump1]
    return control
    