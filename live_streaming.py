# live_streaming.py

from flask import Flask, render_template, Response
from face_recog import get_frame
import socket
import pickle
import struct
import face_recognition
import cv2
import camera
import os
import numpy as np
import datetime
import sys

HOST="116.89.189.30"
PORT=9092

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')
s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn, addr = s.accept()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    data = b""
    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))

    while(True):
        while len(data) < payload_size:
            print("Recv: {}".format(len(data)))
            data += conn.recv(1024)

        print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += conn.recv(1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]


        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        frame = cv2.flip(frame, 0)
        frame = fr.get_frame(frame)

        jpg_bytes1 = cv2.imencode('.jpg', frame)
        jpg_bytes = jpg_bytes1.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':

    app.run(host='127.0.0.1', debug=True)
