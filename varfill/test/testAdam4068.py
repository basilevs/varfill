from adam import Adam4068
from line import Line, DebugLine
from socket import create_connection

if __name__ == '__main__':
    socket = create_connection(("beam-daq", 10002))
    line = Line(socket)
    line = DebugLine(line)
    relay = Adam4068(line, 1)
    for b in [1,0]:
        for ch in range(0,8):
            relay.setChannel(ch, b)
    