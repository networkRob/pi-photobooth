#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from datetime import datetime
from io import BytesIO
from PIL import Image

pic_out = "output/"
file_name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".jpg"

camera = PiCamera()
stream = BytesIO()

# Cameral configurations:
camera.resolution = (3280, 2464)
# camera.rotation = 90 

camera.start_preview()
sleep(2)
#camera.capture(pic_out + file_name)
camera.capture(stream, format="jpeg")
camera.stop_preview()

stream.seek(0)

image = Image.open(stream)

image = image.rotate(90)
image.save(pic_out + file_name)


print("Done!")
