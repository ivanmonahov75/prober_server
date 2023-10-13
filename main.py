import socket
import sys
import time
import multiprocessing as mp
import cv2
import serial
import stm_class


def com_stm(stop, int_data, float_data):  # will be used for sending and receiving data from stm
    test = stm_class.STM_comm(12000000)
    while stop.value == 1:
        pass
    print('STM stopped')
    sys.exit(0)


def com_client(stop, int_stm, float_stm, q_img):  # will be used for two-way communication with client (desktop)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8080))
    server_socket.listen(1)
    while stop.value == 1:
        client_socket, adr = server_socket.accept()
        print(f'connected: {adr}')
        data_got = client_socket.recv(60)
        if data_got:
            new_data = data_got.split()
            if new_data[0] == b'image':
                client_socket.send(q_img.get())
            else:
                client_socket.send(b'error')
        else:
            state = False
        time.sleep(0.03)
    print('Server stopped')
    sys.exit(0)


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
    int_stm_data = mp.Array('i', 10)
    float_stm_data = mp.Array('d', 10)

    queue_img = mp.Queue()

    p_com = mp.Process(target=com_client, args=(_stop, int_stm_data, float_stm_data, queue_img))
    p_cap = mp.Process(target=capturing, args=(_stop, queue_img,))
    p_stm = mp.Process(target=com_stm, args=(_stop, int_stm_data, float_stm_data))

    p_cap.start()
    p_com.start()
    p_stm.start()

    while _stop.value == 1:
        _stop.value = int(input())
        exit(0)

