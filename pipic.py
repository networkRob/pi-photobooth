#!/usr/bin/env python3

from picamera import PiCamera, PiRenderer
from time import sleep
from datetime import datetime

pic_out = "output/"
file_name = datetime.now().strftime("%Y%m%d-%H%M%S")

camera = PiCamera(sensor_mode=2)

# Cameral configurations:
# camera.resolution = (3280, 2464)
camera.rotation = 90 


camera.start_preview()
sleep(2)
camera.capture(pic_out + file_name + ".jpg")
camera.stop_preview()




print("Done!")
