#!/usr/bin/env python3

from flask import Flask, Response
from ObjectDetection_LED import ObjectDetectionLED

TrObj = ObjectDetectionLED()

app = Flask(__name__)

def gen():
    while True:
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + TrObj.gen_frame() + b'\r\n\r\n')

@app.route('/')
def index():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')  

if __name__ == "__main__":
    app.run(host ="192.168.1.39")
