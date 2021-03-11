#!/usr/bin/env python3

from ev3dev2.led import Leds
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, LargeMotor
import cv2
from sys import stderr
from LVC_Camera import LegoVisionCommandCamera

class ObjectDetectionTrack(object):
    def __init__(self):
        self.camera = LegoVisionCommandCamera('/dev/video0')
        self.camera.start_capturing()
        self.ledOn = False
        self.leds = Leds()
        self.leds.set_color('LEFT', 'GREEN')
        self.leds.set_color('RIGHT', 'GREEN')
        self.colorLower = (0, 100, 100)  # define the lower
        self.colorUpper = (10, 255, 255) # and upper boundaries of the "red object" in the HSV color space, then initialize the list of tracked points
        self.panServo = LargeMotor(OUTPUT_A)
        self.tiltServo = LargeMotor(OUTPUT_B)

    def __del__(self):
        del self.camera

    # position servos to present object at center of the frame
    def mapServoPosition(self, x, y):
        rezX = 356/2 - x
        rezY = 292/2 - y

        if abs(rezX) > 20:
            if rezX < 0:
                self.panServo.on_for_degrees(speed=2, degrees=2)
            else: 
                self.panServo.on_for_degrees(speed=-2, degrees=2)
        
        if abs(rezY) > 20:
            if rezY < 0:
                self.tiltServo.on_for_degrees(speed=2, degrees=2)
            else: 
                self.tiltServo.on_for_degrees(speed=-2, degrees=2)
        
        print ("[INFO] Object Center coordenates at X0 = {0} and Y0 = {1}".format(x, y), file=stderr)
        print ("[INFO] Diff -------- coordenates at X0 = {0} and Y0 = {1}".format(rezX, rezY), file=stderr)

    def gen_frame(self):
        # grab the current frame
        frame = cv2.cvtColor(self.camera.read(), cv2.COLOR_BayerGR2RGB)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
        # construct a mask for the color "red", then perform a series of dilations and erosions to remove any small blobs left in the mask
        mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
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
                # draw the circle and centroid on the frame
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

                # position Servo at center of circle
                self.mapServoPosition(int(x), int(y))

                # if the led is not already on, turn the LED on
                if not self.ledOn:
                    self.leds.set_color('LEFT', 'RED')
                    self.leds.set_color('RIGHT', 'RED')
                    self.ledOn = True

        # if the object is not detected, turn the LED off
        elif self.ledOn:
            self.leds.set_color('LEFT', 'GREEN')
            self.leds.set_color('RIGHT', 'GREEN')
            self.ledOn = False
            self.panServo.off(brake=False)
            self.tiltServo.off(brake=False)

        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
