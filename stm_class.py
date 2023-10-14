import serial


class STM_comm():
    def __init__(self, speed, **kwargs):
        super().__init__(**kwargs)
        for i in range(3):
            try:
                self.ser = serial.Serial(f'/dev/ttyACM{i}', 12000000)
                self.opened = True
                return
            except:
                print(f'No /dev/ttyACM{i}')

    def comm(self, adr, *args):
        if self.ser:
            # make bytes array for sending
            mess = adr + '\n'
            self.ser.write(mess)
            # read what we got
            ret = self.ser.readline()
            # modify it to dict
            return ret





