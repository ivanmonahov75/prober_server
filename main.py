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
        float_data[0], int_data[0] = stm.comm(to_stm.value[0:2] + to_stm[2:4] + to_stm[4:6] + to_stm[6:8] + to_stm[8:10] + to_stm[10:12])
    print('STM stopped')
    sys.exit(0)


def com_client(stop, int_stm, float_stm, q_img, to_stm):  # will be used for two-way communication with client (desktop)
    # socket init
    server_socket = socket.socket()
    server_socket.bind(('192.168.1.146', 8080))
    server_socket.listen(1)

    # camera init
    cap = cv2.VideoCapture('/dev/video0')
    while stop.value == 1:
        #ret, frame = cap.read()
        #ret, frame = cv2.imencode('.jpg', frame)

        client_socket, adr = server_socket.accept()
        # print(f'Connected: {adr}')
        data_got = client_socket.recv(3)
        if data_got:
            ret, frame = cap.read()
            ret, frame = cv2.imencode('.jpg', frame)
            client_socket.send(len(frame).to_bytes(3, 'big'))
            client_socket.send(bytes(frame))
            # print(len(frame))

            to_stm.value = b''
            for i in range(6):
                to_stm[i*2:i*2 + 2] = client_socket.recv(2)

            client_socket.send(struct.pack('f', float_stm[0]) + struct.pack('i', int_stm[0]))
            # print((float_stm[0], int_stm[0]))
        time.sleep(0.01)
    print('Server stopped')


def capturing(stop, q):  # just for separate video capture
    cam = cv2.VideoCapture(0)
    while stop.value == 1:
        state, raw_frame = cam.read()
        if not state:
            print('no camera')
            sys.exit(0)
        state, raw_frame = cv2.imencode('.jpg', raw_frame)
        if not state:
            print('camera doesnt work')
            sys.exit(0)
        encoded_image = raw_frame.tobytes()
        while not q.empty():
            test = q.get()
        q.put(encoded_image)  # transfer image to queue, so other tasks can access it
        time.sleep(0.03)
    cam.release()
    print("Capturing stopped")
    sys.exit(0)


if __name__ == '__main__':
    _stop = mp.Value('i', 1)
    int_stm_data = mp.Array('i', 8)
    float_stm_data = mp.Array('d', 2)
    data_to_stm = array = mp.Array(ctypes.c_char, b'\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05')

    queue_img = mp.Queue()

    p_com = mp.Process(target=com_client, args=(_stop, int_stm_data, float_stm_data, queue_img, data_to_stm))
    p_cap = mp.Process(target=capturing, args=(_stop, queue_img,))  # currently not in use
    p_stm = mp.Process(target=com_stm, args=(_stop, int_stm_data, float_stm_data, data_to_stm))

    # p_cap.start()
    p_com.start()
    p_stm.start()
    while _stop.value == 1:
        _stop.value = int(input())
        exit(0)
