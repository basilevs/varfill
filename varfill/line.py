from datetime import datetime, timedelta
from socket import MSG_DONTWAIT, MSG_WAITALL, error as socket_error, timeout as socket_timeout
from errno import EAGAIN
from threading import Lock

class Timeout(RuntimeError):
    pass

def tryUntilTimeout(action, timeout):
    """ Tries perform action until timeout is reached
        timeout argument should be of type timedelta
        Action should:
        - accept a single argument - time until final timeout
        - return false value if tries should be continued
        Returns last action result
    """
    assert(isinstance(timeout, timedelta))
    until = datetime.now() + timeout
    while True:  
        rv = action(timeout)
        if rv:
            return rv
        timeout = until - datetime.now()
        if timeout < timedelta(0):
            return rv

def tohex(data):
    rv=""
    for b in data:
        rv+="%02X" % b
    return rv

        
class Line(object):
    def __init__(self, socket):
        self.__socket__ = socket
        self.__buffer__ = bytearray()
        self.lock = Lock()
    def readWithTimeout(self, timeout):
        """Reads socket into buffer until at least one byte is read or timeout is expired."""
        assert(isinstance(timeout, timedelta))
        socket = self.__socket__
        try:
            self.__buffer__ += socket.recv(4096, MSG_DONTWAIT)
            return
        except socket_error as e:
            if e.errno != EAGAIN:
                raise
        oldtimeout = socket.gettimeout()
        try:
            socket.settimeout(timeout.total_seconds())
            #print("Waiting")
            self.__buffer__ += socket.recv(1, MSG_WAITALL)
        except socket_timeout as e:
            return
        except socket_error as e:
            if e.errno == EAGAIN:
                return
            raise       
        finally:
            socket.settimeout(oldtimeout)
                    
    def readline(self, timeout, delimiter=b'\r'):
        assert(isinstance(timeout, timedelta))
        def tryReadLine(timeout):
            def processBuf():
                eolPosition = self.__buffer__.find(delimiter)
                if eolPosition >= 0:
                    line = self.__buffer__[0:eolPosition]
                    self.__buffer__ = self.__buffer__[eolPosition + len(delimiter):]
                    return line
                return None
            line = processBuf()
            if line:
                return line
            self.readWithTimeout(timeout)
            return processBuf()
        line = tryUntilTimeout(tryReadLine, timeout)
        if not line:
            raise Timeout("Line read timeout. Data read so far: " + str(self.__buffer__))
        return line
    
    def write(self, data):
        socket = self.__socket__
        oldtimeout = socket.gettimeout()
        try:
            self.__socket__.sendall(data)
        finally:
            socket.settimeout(oldtimeout)    

class DebugLine(object):
    def __init__(self, line, prefix=""):
        self.__line__ = line
        self.prefix = prefix
        self.lock = Lock()
    def setTimeout(self, timeout):
        self.__line__.tiemout = timeout
    timeout = property(lambda self: self.__line__.timeout, setTimeout)
    def write(self, data):
        print(self.prefix,"sending ",tohex(data))
        self.__line__.write(data)
    def readline(self, timeout, delimiter=b'\r'):
        rv = self.__line__.readline(timeout, delimiter)
        print(self.prefix,"read line",tohex(rv))
        return rv
    def readWithTimeout(self, timeout):
        rv = self.__line__.readWithTimeout(timeout)
        print(self.prefix,"read ",tohex(rv))
        return rv
    
