#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from datetime import datetime

pic_out = "output/"
file_name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".jpg"

camera = PiCamera()

# Cameral configurations:
camera.resolution = (2592, 1944)
camera.rotation = 90 

camera.start_preview()
sleep(5)
camera.capture(pic_out + file_name)
camera.stop_preview()

print("Done!")
