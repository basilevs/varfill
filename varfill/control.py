from socket import create_connection
from line import Line
from adam import Adam4024
from sys import argv
from getopt import getopt
from time import sleep
from piv import Kshd, Piv
from datetime import datetime, timedelta

class Mover(object):
    def __init__(self):
        self.maxTravel = -10000000 
    def setSpeed(self, speed):
        raise NotImplementedError
    def start(self):
        self.go(10000000)
    def stop(self):
        raise NotImplementedError
    def getPosition(self):
        raise NotImplementedError
    
class KshdMover(Mover):
    def __init__(self, kshd):
        assert(isinstance(kshd,Kshd))
        self.__kshd__ = kshd
    def setSpeed(self, speed):
        s = self.__kshd__.getSpeed()
        s.max = speed
        self.__kshd__.setSpeed(s)
    def go(self, steps):
        self.__kshd__.go(steps)
    def stop(self):
        self.__kshd__.stop()
    def getPosition(self):
        return self.__kshd__.getPosition()

class Control(object):
    def __init__(self):
        self.pumps=[]
        self.mover=Mover()
        def dummy(seconds, pumpValues):
            pass
        self.stepCallback=dummy
        self.stopRequest = True
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
        if not self.stopRequest:
            raise RuntimeError("Already running")           
        self.stopRequest = False
        self.mover.setSpeed(moveSpeed)
        start = datetime.now()
        until = start + timedelta(seconds = time)
        self.mover.start()
        while datetime.now() < until:
            if self.stopRequest:
                break
            seconds = (datetime.now() - start).total_seconds();
            values = calcPumpValues(seconds)
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
        adam1.setChannel(3, value)
    def pump2(value):
        print("Set pump2 to:", value)
    control.pumps = [pump1]
    return control

def mockControl():
    control = Control()
    
    class MoverMock(Mover):
        def __init__(self):
            self.startTime = None
            self.position = 0
            self.speed = 100
        def setSpeed(self, speed):
            self.speed = speed
            print("Speed",speed)
        def start(self):
            self.startTime = datetime.now()
            print("Mover start")
        def stop(self):
            self.position = self.getPosition()
            self.startTime = None
            print("Mover stop")
        def go(self, steps):
            if self.startTime:
                raise RuntimeError("The motor is moving now")
            self.position += steps
            print("Moved to:", self.position)
        def getPosition(self):
            if self.startTime:
                return self.position + self.speed * (datetime.now() - self.startTime).total_seconds()
            return self.position
            
    control.mover = MoverMock()
    def pump1(value):
        sleep(0.1)
        print("Pump1: "+str(value))
    def pump2(value):
        sleep(0.1)
        print("Pump2: "+str(value))
        
    control.pumps=[pump1, pump2]
    return control
    