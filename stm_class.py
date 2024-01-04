import struct

import serial



class STM_comm():
    def __init__(self, speed):
        self.opened = None
        self.adr_press = (1).to_bytes(1, 'big')
        self.adr_temp = (2).to_bytes(1, 'big')
        for i in range(3):
            try:
                self.ser = serial.Serial(f'/dev/ttyACM{i}', 12000000)
                self.opened = True
                print(f'Connected at /dev/ttyACM{i}')
                return
            except:
                print(f'No /dev/ttyACM{i}')

    def comm(self, data=b'\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05'):
        if len(data) < 12:
            data = b'\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05'
        if self.opened:
            self.ser.write(data)
            temperature = round(struct.unpack('f', self.ser.read(4))[0], 4)
            pressure = struct.unpack('i', self.ser.read(4))[0]
            return temperature, pressure
        return self.opened






