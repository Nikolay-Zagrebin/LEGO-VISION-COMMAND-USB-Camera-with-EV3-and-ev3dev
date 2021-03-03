#!/usr/bin/env python3

from fcntl import ioctl
import v4l2
import mmap
import numpy as np

class LegoVisionCommandCamera(object):
    def __init__(self, device_name):
        self.device_name = device_name
        self.nub_buffers = 3
        self.buffers = []
        self.open_device()
        self.init_device()
        self.init_mmap()

    def open_device(self):
        self.fd = open(self.device_name, 'rb+', buffering=0)
    
    def close_device(self):
        buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        ioctl(self.fd, v4l2.VIDIOC_STREAMOFF, buf_type)
        self.fd.close()
        
    def init_device(self):
        fmt = v4l2.v4l2_format()
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        ioctl(self.fd, v4l2.VIDIOC_G_FMT, fmt)
        ioctl(self.fd, v4l2.VIDIOC_S_FMT, fmt)

    def init_mmap(self):
        self.req = v4l2.v4l2_requestbuffers()      
        self.req.count = self.nub_buffers
        self.req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        self.req.memory = v4l2.V4L2_MEMORY_MMAP 
        ioctl(self.fd, v4l2.VIDIOC_REQBUFS, self.req)

        for x in range(self.req.count):
            buf = v4l2.v4l2_buffer()
            buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = v4l2.V4L2_MEMORY_MMAP
            buf.index = x
            
            ioctl(self.fd, v4l2.VIDIOC_QUERYBUF, buf)

            buf.buffer =  mmap.mmap(self.fd.fileno(), buf.length, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=buf.m.offset)
            self.buffers.append(buf)

    def start_capturing(self):
        for buf in self.buffers:
            ioctl(self.fd, v4l2.VIDIOC_QBUF, buf)
        buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        ioctl(self.fd, v4l2.VIDIOC_STREAMON, buf_type)

    def read(self):
        while True:
            for x in range(self.req.count):
                buf = self.buffers[x]
                ioctl(self.fd, v4l2.VIDIOC_DQBUF, buf)
                mm = self.buffers[buf.index].buffer
                raw_data = mm.read(buf.bytesused)
                mm.seek(0)
                yield np.frombuffer(raw_data, dtype=np.uint8).reshape((292, 356))
                ioctl(self.fd, v4l2.VIDIOC_QBUF, buf)
