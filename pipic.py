#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from datetime import datetime
from io import BytesIO
from PIL import Image

pic_out = "output/"
file_name = datetime.now().strftime("%Y%m%d-%H%M%S")

camera = PiCamera()
stream = BytesIO()

# Cameral configurations:
camera.resolution = (3280, 2464)
camera.rotation = 90 

def cropImg(pImg):
    w, h = pImg.size
    nimg = pImg.crop((w*.1, 0, w*.8, h))
    return(nimg)

camera.start_preview()
sleep(2)
camera.capture(pic_out + file_name + ".jpg")
# camera.capture(stream, format="jpeg")
camera.stop_preview()

# stream.seek(0)

# image = Image.open(stream)
image = Image.open(pic_out + file_name + ".jpg")

# image.save(pic_out + file_name + ".jpg")

nimg = cropImg(image)
nimg.save(pic_out + file_name + "-edit.jpg")


print("Done!")
