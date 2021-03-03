#!/usr/bin/env python3

from PIL import Image
from ev3dev2.display import Display
from time import sleep
from LVC_Camera import LegoVisionCommandCamera

if __name__ == "__main__":
    lcd = Display()
    cam = LegoVisionCommandCamera('/dev/video0')
    cam.start_capturing()
    read_task = cam.read()
    while True:
        np_data = next(read_task)

        PIL_image = Image.fromarray(np_data).resize((356//2, 292//2)).crop((0, 0, 178, 128))
        #fn = lambda x : 255 if x > 128 else 0
        #PIL_image = PIL_image.convert('L').point(fn, mode='1')
        PIL_image = PIL_image.convert('1')

        lcd.image.paste(PIL_image, (0,0))
        lcd.update()
        sleep(0.1)
        #PIL_image.save('PIL_img.png')

    cam.close_device()
