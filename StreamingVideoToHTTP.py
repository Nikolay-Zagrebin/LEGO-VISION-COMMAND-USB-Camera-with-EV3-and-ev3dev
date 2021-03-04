#!/usr/bin/env python3

from flask import Flask, Response
import cv2
from LVC_Camera import LegoVisionCommandCamera

camera = LegoVisionCommandCamera('/dev/video0')
camera.start_capturing()
read_task = camera.read()

app = Flask(__name__)

def gen():
    while True:
        np_data = next(read_task)
        image = cv2.cvtColor(np_data, cv2.COLOR_BayerGR2RGB)
        ret, jpeg = cv2.imencode('.jpg', image)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host ="192.168.1.39")
