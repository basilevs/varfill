from time import sleep
from struct import unpack

class PivError(RuntimeError):
    pass

class BadPivPacket(PivError):
    pass

class BadPivModuleType(PivError):
    pass

class BadPivRelpy(PivError):
    pass

def calcControl(data):
    rv = 0
    for b in data:
        rv ^= b
    return rv

class Piv(object):
    '''
    Volkov's protocol
    '''
    cstart = b'\xAA'
    cstop = b'\xAB'
    cshift = b'\xAC'
    escapedSymbols = (cstart, cstop, cshift)
    def __init__(self, line):
        self.__line__ = line
        
    def send(self, address, data):
        assert(isinstance(address, int))
        assert(address >= 0)
        assert(address < 256)
        body = bytearray()
        body.append(address)
        body += data        

        control = calcControl(body)
        assert(control < 256)
             
        buffer = bytearray()        
        buffer += Piv.cstart
        for b in body:
            assert(b >=0 and b < 256)
            if b in Piv.escapedSymbols:
                buffer += Piv.cshift
                buffer.append(b - Piv.cstart[0])
            else:
                buffer.append(b)
        buffer.append(control)
        buffer += Piv.cstop
        self.__line__.write(buffer)
    def receive(self, address):
        assert(isinstance(address, int))   
        data = self.__line__.readline(Piv.cstop)
        if len(data) < 2:
            raise BadPivPacket(("Piv packet is too short", data))
        converted = bytearray()
        shifted = False
        for b in data:
            if b == Piv.cshift[0]:
                if shifted:
                    raise BadPivPacket(("Invalid shift", data))
                shifted = True
                continue
            if shifted:
                if b < Piv.cstart[0] or b in Piv.escapedSymbols:
                    raise BadPivPacket(("Invalid shift", data))                    
                b += Piv.cstart[0]
            shifted = False
            assert(b >=0 and b < 256)
            converted.append(b)
        body = converted[0:-1]
        control = calcControl(body)
        if control != converted[-1]:
            raise BadPivPacket(("Bad control sum", converted))
        if body[0] != address:
            raise BadPivPacket(("Invalid address", data))
        return data[1:len(data)-1]

class PivModule(object):
    def __init__(self, piv, address):
        self.__piv__ = piv
        self.__address__ = address
    def query(self, data):
        self.__piv__.send(self.__address__, data)
        return self.__piv__.receive(self.__address__)

class Kshd(PivModule):
    def __init__(self, piv, address):
        PivModule.__init__(self, piv, address)
        data = self.query(b'\x01')
        if data[0:2] != b'WS':
            raise BadPivModuleType(data)
    class Status(object):
        def __init__(self, b):
            b = int(b)
            self.__b__ = b
            rv = self
            rv.ready = b & 1
            rv.moving = b & 2
            rv.atMinus = b & 4
            rv.atPlus = b & 8
            rv.atZero = b & 16
            rv.exactSpeed = b & 32
        def __repr__(self):
            return "piv.Kshd.Status(0x%X)" % self.__b__
    def status(self):
        b = self.query(b'\x03')
        if len(b) != 1:
            raise BadPivRelpy(b)
        b = int(b[0])
        return Kshd.Status(b)
    def waitReady(self):
        while(not self.status().ready):
            sleep(0.1)
            pass
    def writeInt(self, n, byteCount=4):
        n = int(n)
        rv = bytearray()
        for i in range(byteCount):
            rv.append(((n & 0xFF) >> ((byteCount-i) * 8))  & 0xFF)
        assert(len(rv)==byteCount)
        return rv
    def readInt(self, data):
        byteCount = len(data)
        rv = 0
        for i in range(byteCount):
            rv |= ((data[i] & 0xFF) << ((byteCount-i)*8))
        return rv
    def goWithSpeed(self, steps, stepTime):
        b = self.query(b'\x11'+self.writeInt(steps)+self.writeInt(stepTime))
        return Kshd.Status(b[0])
    def getCoordinate(self):
        data = self.query(b'\x14')
        
        rv = self.readInt(data)
        if rv == 0x80000000:
            raise BadPivRelpy("Invalid coordinate")
        return rv 
        
