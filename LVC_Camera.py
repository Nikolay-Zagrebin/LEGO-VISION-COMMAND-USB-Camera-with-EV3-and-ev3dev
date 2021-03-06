#!/usr/bin/env python3

from fcntl import ioctl
import v4l2
import mmap
import numpy as np
from threading import Thread, Event
from sys import stderr
from ev3dev2.button import Button
from time import sleep

class MonitorButton(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.shutdown_event = Event()
        self.btn = Button()

    def __str__(self):
        return "MonitorButton"
    
    def check_exposure(self, exposure):
        if exposure > 32768:
            exposure = 32768
        if exposure < 0:
            exposure = 0
        return exposure
    
    def check_gain(self, gain):
        if gain > 15:
            gain = 15
        if gain < 0:
            gain = 0
        return gain

    def run(self):
        while True:
            if self.btn.up:
                self.parent.exposure += 500
                self.parent.exposure = self.check_exposure(self.parent.exposure)
                self.parent.set_param()
                print('exposure: ' + str(self.parent.exposure))
                print('exposure: ' + str(self.parent.exposure), file=stderr)

            if self.btn.down:
                self.parent.exposure -= 500
                self.parent.exposure = self.check_exposure(self.parent.exposure)
                self.parent.set_param()
                print('exposure: ' + str(self.parent.exposure))
                print('exposure: ' + str(self.parent.exposure), file=stderr)

            if self.btn.left:
                self.parent.gain -= 1
                self.parent.gain = self.check_gain(self.parent.gain)
                self.parent.set_param()
                print('gain: ' + str(self.parent.gain))
                print('gain: ' + str(self.parent.gain), file=stderr)

            if self.btn.right:
                self.parent.gain += 1
                self.parent.gain = self.check_gain(self.parent.gain)
                self.parent.set_param()
                print('gain: ' + str(self.parent.gain))
                print('gain: ' + str(self.parent.gain), file=stderr)

            if self.shutdown_event.is_set():
                break

            sleep(0.1)

class LegoVisionCommandCamera(object):
    def __init__(self, device_name):
        self.device_name = device_name
        self.exposure = 20000   # min=0 max=32768 step=1 default=20000
        self.gain = 10          # min=0 max=15 step=1 default=10
        self.open_device()
        self.set_param()
        self.init_mmap()
        self.mb = MonitorButton(self)
        self.shutdown_event = Event()

    def __del__(self):
        buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        ioctl(self.fd, v4l2.VIDIOC_STREAMOFF, buf_type)
        self.fd.close()

    def open_device(self):
        self.fd = open(self.device_name, 'rb+', buffering=0)
        
    def set_param(self):
        #fmt = v4l2.v4l2_format()
        #fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        #ioctl(self.fd, v4l2.VIDIOC_G_FMT, fmt)
        #ioctl(self.fd, v4l2.VIDIOC_S_FMT, fmt)

        control = v4l2.v4l2_control()
        control.id = v4l2.V4L2_CID_EXPOSURE
        control.value = self.exposure
        ioctl(self.fd, v4l2.VIDIOC_S_CTRL, control)

        control = v4l2.v4l2_control()
        control.id = v4l2.V4L2_CID_GAIN
        control.value = self.gain
        ioctl(self.fd, v4l2.VIDIOC_S_CTRL, control)

    def init_mmap(self):
        req = v4l2.v4l2_requestbuffers()      
        req.count = 1
        req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        req.memory = v4l2.V4L2_MEMORY_MMAP 
        ioctl(self.fd, v4l2.VIDIOC_REQBUFS, req)

        self.buf = v4l2.v4l2_buffer()
        self.buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        self.buf.memory = v4l2.V4L2_MEMORY_MMAP
        self.buf.index = 0
            
        ioctl(self.fd, v4l2.VIDIOC_QUERYBUF, self.buf)

        self.buf.buffer = mmap.mmap(self.fd.fileno(), self.buf.length, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=self.buf.m.offset)

    def start_capturing(self):
        ioctl(self.fd, v4l2.VIDIOC_QBUF, self.buf)
        buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        ioctl(self.fd, v4l2.VIDIOC_STREAMON, buf_type)
        self.mb.start()
        #self.shutdown_event.wait()

    def read(self):
        ioctl(self.fd, v4l2.VIDIOC_DQBUF, self.buf)
        raw_data = self.buf.buffer.read(self.buf.bytesused)
        self.buf.buffer.seek(0)
        ioctl(self.fd, v4l2.VIDIOC_QBUF, self.buf)

        return np.frombuffer(raw_data, dtype=np.uint8).reshape((292, 356))
