

class PivError(RuntimeError):
    pass

class BadPivPacket(PivError):
    pass

class BadPivModuleType(PivError):
    pass

class Piv(object):
    '''
    Volkov's protocol
    '''
    cstart = b'\xAA'
    cstop = b'\xAB'
    cshift = b'\xAC'
    escapedSymbols = (Piv.cstart, Piv.cstop, Piv.cshift)
    def __init__(self, line):
        self.__line__ = line
        self.__buffer__ = bytearray()
    def send(self, address, data):
        assert(isinstance(address, int))   
        buffer = bytearray()
        buffer += Piv.cstart
        control = 0
        for b in data:
            assert(b >=0 and b < 256)
            if b in Piv.escapedSymbols:
                buffer += Piv.cshift
                buffer.append(b - Piv.cstart[0])
            else:
                buffer.append(b)
            control ^= b
        assert(control < 256)
        buffer.append(control)
        buffer += Piv.stop
        self.__line__.send(buffer)
    def receive(self, address):
        assert(isinstance(address, int))   
        data = self.__line__.readline(Piv.cstop)
        if len(data) < 2:
            raise BadPivPacket(("Piv packet is too short", data))
        converted = bytearray()
        shifted = False
        control = 0
        for b in data:
            if b == Piv.cshift[0]:
                shifted = True
                continue
            if shifted:
                b += Piv.cstart[0]
            shifted = False
            assert(b >=0 and b < 256)
            control ^= b
            converted.append(b)
        data = converted
        if data[0] != address:
            raise BadPivPacket(("Invalid address", data))
        if control != data[len(data)-1]:
            raise BadPivPacket(("Bad control sum", data))
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
        data = self.query(b'\x1')
        if data[0:2] != b'WS':
            raise BadPivModuleType(data)
    
        
        
        
