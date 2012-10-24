import unittest
import socket
from socket import error as socket_error, timeout as socket_timeout, create_connection
from time import sleep
import unittest
from threading import Thread
from errno import ECONNREFUSED
from datetime import datetime, timedelta
from line import Line, PersistentSocket

class EchoServer(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.__socket__ = socket
        self.start()
    def close(self):
        s=self.__socket__
        self.__socket__=None
        s.close()
    def run(self):
        start = datetime.now()
        try:
            while (datetime.now() - start).total_seconds() < 2:
                if not self.__socket__:
                    break
                data = self.__socket__.recv(1)
                if len(data):
                    self.__socket__.sendall(data)
        except socket_error as e:
            if not e.errno in (104, 9):
                raise
                
            
                            

class Accept(Thread):
    def __init__(self, address, server):
        Thread.__init__(self)
        self.address = address
        self.server = server
        self.servers = []
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind(self.address)
        except socket_error:
            print(self.address)
            raise
        self.socket.listen(1)        
        self.start()
        sleep(0.1)
    def close(self):
        ss = self.servers
        self.servers = []
        for s in ss:
            s.close()
        self.socket.close()
    def run(self):
        print("Waiting on",self.address)
        self.servers.append(self.server(self.socket.accept()[0]))
        print("Accepted on",self.address)

        
class LineTest(unittest.TestCase):
    host = "127.0.0.1"
    port = 46519
    def address(self):
        LineTest.port +=1
        return (LineTest.host, LineTest.port)
    def test_connFail(self):
        self.assertRaises(socket_error, PersistentSocket, self.address())        
    def test_simpleLine(self):
        address = self.address()
        accept = self.serve(address)
        client=create_connection(address)
        try:
            data = b'sdafsf454534\n'
            line = Line(client)
            line.write(data)
            l = line.readline(timedelta(seconds=1), b'\n')
            self.assertEqual(data, l+b'\n')
        finally:
            client.close()
            accept.close()
    def serve(self, address):
        return Accept(address, EchoServer)
