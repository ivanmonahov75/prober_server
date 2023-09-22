import multiprocessing
import socket
import sys
import time
from multiprocessing import Process
import cv2


def com_stm():  # will be used for sending and receiving data from stm
    pass


def com_client(q_stm, q_img):  # will be used for two-way communication with client (desktop)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8080))
    server_socket.listen(1)
    while True:
        client_socket, adr = server_socket.accept()
        print(f'connected: {adr}')
        state = True
        while state:
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


def capturing(q):  # just for separate video capture
    cam = cv2.VideoCapture(0)
    while True:
        state, raw_frame = cam.read()
        if not state:
            print('somthing went wrong')
            sys.exit(0)
        state, raw_frame = cv2.imencode('.jpg', raw_frame)
        if not state:
            print('somthing went wrong')
            sys.exit(0)
        encoded_image = raw_frame.tobytes()
        q.empty()
        q.put(encoded_image)  # transfer image to queue, so other tasks can access it
        time.sleep(0.03)


if __name__ == '__main__':
    queue_img = multiprocessing.Queue()
    queue_stm_data = multiprocessing.Queue()
    p_com = Process(target=com_client, args=(queue_stm_data, queue_img))
    p_cap = Process(target=capturing, args=(queue_img,))
    p_stm = Process(target=com_stm, args=(queue_stm_data,))
    p_cap.start()
    p_com.start()
