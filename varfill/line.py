from datetime import datetime, timedelta
from socket import MSG_DONTWAIT, MSG_WAITALL, error as socket_error, timeout as socket_timeout
from errno import EAGAIN

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

        
class Line(object):
    def __init__(self, socket):
        self.__socket__ = socket
        self.timeout = timedelta(seconds=1)
        self.__buffer__ = bytearray()
    def readWithTimeout(self, timeout):
        """Reads socket until at least one byte is read or timeout (in seconds) is expired."""
        socket = self.__socket__
        try:
            self.__buffer__ += socket.recv(4096, MSG_DONTWAIT)
        except socket_error as e:
            if e.errno != EAGAIN:
                raise
        oldtimeout = socket.gettimeout()
        try:
            socket.settimeout(timeout)
            self.__buffer__ += socket.recv(1, MSG_WAITALL)
        except socket_timeout as e:
            return
        except socket_error as e:
            if e.errno == EAGAIN:
                return
            raise       
        finally:
            socket.settimeout(oldtimeout)
                    
    def readline(self, delimiter=b'\r'):
        def tryReadLine(timeout):
            eolPosition = self.__buffer__.find(delimiter)
            if eolPosition >= 0:
                line = self.__buffer__[0:eolPosition]
                self.__buffer__ = self.__buffer__[eolPosition + len(delimiter):]
                return line
            self.readWithTimeout(timeout.total_seconds())
            return None            
        line = tryUntilTimeout(tryReadLine, self.timeout)
        if not line:
            raise Timeout("Line read timeout. Data read so far: " + self.__buffer__.decode("utf-8"))
        return line
    
    def write(self, data):
        socket = self.__socket__
        oldtimeout = socket.gettimeout()
        try:
            self.__socket__.sendall(data)
        finally:
            socket.settimeout(oldtimeout)    
