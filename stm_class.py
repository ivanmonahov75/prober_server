import struct

import serial



class STM_comm():
    def __init__(self, speed):
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

    def get_data(self):
        data = {'press' : 0, 'temp': 0}
        if self.opened:
            self.ser.write(self.adr_press)
            data['press'] = int.from_bytes(self.ser.read(4), 'little')/1000
            self.ser.write(self.adr_temp)
            data['temp'] = struct.unpack('f', self.ser.read(4))
            return data
        return self.opened






