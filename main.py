import socket
import sys
import time
import multiprocessing as mp
import cv2
import serial
import stm_class
import struct
import ctypes


def com_stm(stop, flag, float_data, to_stm):  # will be used for sending and receiving data from stm
    stm = stm_class.STM_comm(12000000)
    while stop.value == 1:
        if flag.value == 1:
            float_data = stm.comm(to_stm.value[0:2] + to_stm[2:4] + to_stm[4:6] + to_stm[6:8] + to_stm[8:10] + to_stm[10:12])
            print(float_data[0])
            flag.value = 0
    print('STM stopped')
    sys.exit(0)


def com_client(stop, flag, float_stm, q_img, to_stm):  # will be used for two-way communication with client (desktop)
    # camera init
    cap = cv2.VideoCapture('/dev/video0')
    while stop.value == 1:
        # socket reg init
        socket_server = socket.socket()
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.bind(('192.168.1.146', 8080))
        socket_server.listen(1)

        socket_client, adr = socket_server.accept()

        # add getting data for st
        data_to_stm = socket_client.recv(12)

        # camera usage
        ret, frame = cap.read()
        ret, frame = cv2.imencode('.jpg', frame)
        socket_client.send(len(frame).to_bytes(3, 'big'))
        socket_client.send(frame)

        # send data from stm
        socket_client.send(struct.pack('f', float_stm[0]))
        print(float_stm[0])
        print(struct.pack('f', float_stm[0]))
        socket_client.send(b'\x90_\x01\x00')

        # shutdown socket
        socket_server.shutdown(1)
        socket_server.close()
        flag.value = 1
    print('Server stopped')



if __name__ == '__main__':
    _stop = mp.Value('i', 1)
    flag_for_stm = mp.Value('i', 1)
    float_stm_data = mp.Array('d', 2)
    data_to_stm = array = mp.Array(ctypes.c_char, b'\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05')

    queue_img = mp.Queue()

    p_com = mp.Process(target=com_client, args=(_stop, flag_for_stm, float_stm_data, queue_img, data_to_stm))
    p_stm = mp.Process(target=com_stm, args=(_stop, flag_for_stm, float_stm_data, data_to_stm))

    p_com.start()
    p_stm.start()
    while _stop.value == 1:
        _stop.value = int(input())
        exit(0)
