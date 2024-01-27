import socket
import sys
import time
import multiprocessing as mp
import cv2
import serial
import stm_class
import struct
import ctypes


def com_stm(stop, int_data, float_data, to_stm):  # will be used for sending and receiving data from stm
    stm = stm_class.STM_comm(12000000)
    while stop.value == 1:
       # float_data[0], int_data[0] = stm.comm(to_stm.value[0:2] + to_stm[2:4] + to_stm[4:6] + to_stm[6:8] + to_stm[8:10] + to_stm[10:12])
        pass
    print('STM stopped')
    sys.exit(0)


def com_client(stop, int_stm, float_stm, q_img, to_stm):  # will be used for two-way communication with client (desktop)
    # camera init
    cap = cv2.VideoCapture('/dev/video0')
    while stop.value == 1:
        # socket reg init
        socket_server = socket.socket()
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.bind(('192.168.1.146', 8080))
        socket_server.listen(1)

        socket_client, adr = socket_server.accept()

        # add getting data for stm
        for i in range(6):
            data_to_stm[i*2:i*2 + 2] = socket_client.recv(2)

        # camera usage
        ret, frame = cap.read()
        ret, frame = cv2.imencode('.jpg', frame)
        socket_client.send(len(frame).to_bytes(3, 'big'))
        socket_client.send(frame)

        socket_server.shutdown(1)
        socket_server.close()
    print('Server stopped')



if __name__ == '__main__':
    _stop = mp.Value('i', 1)
    int_stm_data = mp.Array('i', 8)
    float_stm_data = mp.Array('d', 2)
    data_to_stm = array = mp.Array(ctypes.c_char, b'\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05')

    queue_img = mp.Queue()

    p_com = mp.Process(target=com_client, args=(_stop, int_stm_data, float_stm_data, queue_img, data_to_stm))
    p_stm = mp.Process(target=com_stm, args=(_stop, int_stm_data, float_stm_data, data_to_stm))

    p_com.start()
    p_stm.start()
    while _stop.value == 1:
        _stop.value = int(input())
        exit(0)
