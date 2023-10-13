import serial


class STM_comm(serial.Serial):
    def __init__(self, speed, **kwargs):
        super().__init__(**kwargs)
        for i in range(3):
            try:
                self.Serial(f'/dev/ttyACM{i}', speed)
                self.opened = True
                return
            except:
                print(f'No /dev/ttyACM{i}')

    def comm(self, adr, *args):
        if self.Serial:
            # make bytes array for sending
            mess = adr + '\n'
            self.write(mess)
            # read what we got
            ret = self.readline()
            # modify it to dict
            return ret





