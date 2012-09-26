from line import Adam4068, Line
from socket import create_connection

if __name__ == '__main__':
    socket = create_connection(("beam-daq", 10002))
    line = Line(socket)
    relay = Adam4068(line, 1)
    relay.setChannel(6, True)
    