#!/usr/bin/env python3

#from collections import deque
import cv2
from LVC_Camera import LegoVisionCommandCamera

class TrackingObject(object):
    def __init__(self):
        self.camera = LegoVisionCommandCamera('/dev/video0')
        self.camera.start_capturing()
        self.read_task = self.camera.read()

    def __del__(self):
        self.camera.close_device()

    def gen_frame(self):
        # define the lower and upper boundaries of the "red object" in the HSV color space, then initialize the list of tracked points
        colorLower = (0, 100, 100)
        colorUpper = (5, 255, 255)
        
        # grab the current frame
        np_data = next(self.read_task)
        frame = cv2.cvtColor(np_data, cv2.COLOR_BayerGR2RGB)
    
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
        # construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
	
        # find contours in the mask and initialize the current (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
 
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame, then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
        # save the frame
        # cv2.imwrite('test.jpg', frame)
        #gh = False
