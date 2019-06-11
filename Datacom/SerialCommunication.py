import serial
from time import sleep
import zmq

# setup zmq socket server
context = zmq.Context()
zmqsocket = context.socket(zmq.REP)
zmqsocket.bind("tcp://127.0.0.1:7777")

# setup serial communication with printer
port = "/dev/ttyUSB0"
s1 = serial.Serial(port, 115200)
sleep(2)
s1.flushInput()

delchars = dict.fromkeys(map(ord, 'okT:/B@'), None)

while True:
    c = zmqsocket.recv()
    command = c['command']

    gcode = ""
    if command == 'G28':
        gcode = 'G28'
        if 'x' in c['axis']:
            gcode += ' X'
        if 'y' in c['axis']:
            gcode += ' Y'
        if 'z' in c['axis']:
            gcode += ' Z'

    elif command == 'G1':
        gcode = 'G1'
        if 'x' in c['axis']:
            gcode += ' X'
        elif 'y' in c['axis']:
            gcode += ' Y'
        elif 'z' in c['axis']:
            gcode += ' Z'

        if c['negative']:
            gcode += '-'

        gcode += c['value']

    elif command == 'M18':
        gcode = 'M18'

    elif command == 'M106':
        gcode = 'M106'

    elif command == 'M107':
        gcode = 'M107'

    else:
        print("no known command or 'command' is null")
        gcode = c


    print("send: ", '{}\n'.format(gcode).encode())
    s1.write('{}\n'.format(gcode).encode())
    sleep(0.02)

    if s1.inWaiting() > 0:
        inputValue = s1.readline()
        s = str(inputValue.decode())
        if s.strip():
            print("ack: ", s.strip())
            if s.strip() == "ok":
                zmqsocket.send(s.strip())
            else:
                s = list(map(float, s.translate(delchars).strip().split(' ')))
                zmqsocket.send(s)
