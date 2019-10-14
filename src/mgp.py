#!/usr/bin/env python3

"""
DESCRIPTION
A Python socket server to act as a backend service for 
Raspberrypi ZeroW web based photobooth.

"""
__author__ = 'Rob Martin'
__version__ = 0.3

# import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import json
from os import getcwd
from subprocess import Popen, PIPE
from PIL import Image, ImageFont, ImageDraw
from picamera import PiCamera
from time import sleep
from datetime import datetime, timedelta

l_port = 8888
pi_resolution = (1772, 1181)
# pi_resolution = (1181, 1772)
pic_out = "html/pb-imgs/"
UPLOADER = "./dropbox_uploader.sh"
UPLOAD_DESTINATION = "mTest/"
# Number of photos to take
PHOTOSTRIP = 3
FINALWIDTH = 800
FINALHEIGHT = 800
BORDERWIDTH = 10
# Party Specific
PMESSAGE = "Finley's 2 Wild Birthday Party!\n10/19/2019"
PLOGO = "imgs/fin-logo.jpg"

def getDATETIME():
    return(datetime.now().strftime("%Y%m%d-%H%M%S"))

class cameraRequestHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("New connection from: {}".format(self.request.remote_ip))
        self.write_message(json.dumps({'type':'hello','data':"hello user"}))

    def on_message(self,message):
        print("[{0}] Sent: {1}".format(self.request.remote_ip,message))
        self.countdown()

    def countdown(self):
        picam = activateCamera()
        photo_strip = []
        pIND = 0
        base_filename = getDATETIME()
        while pIND < PHOTOSTRIP:
            count_down = 3
            while count_down > 0:
                self.write_message(json.dumps({'type':'countdown','data':count_down}))
                sleep(1)
                count_down -= 1
            self.write_message(json.dumps({'type':'countdown','data':'Cheese!'}))
            cam_result = takePicture(picam,base_filename + "-{}".format(pIND + 1))
            self.write_message(json.dumps({'type':'countdown','data':'Picture taken!'}))
            # Upload photo to Dropbox App
            uploadPicture(cam_result['path'])
            photo_strip.append(cam_result['path'])
            print("Pictures saved to pb-imgs/{}".format(cam_result['name']))
            pIND += 1
            if pIND < PHOTOSTRIP:
                self.write_message(json.dumps({
                    'type':'countdown',
                    'data':'Here we go again!<br />{} more to go...'.format(PHOTOSTRIP - pIND)
                }))
                sleep(2)
        if photo_strip:
            self.write_message(json.dumps({'type':'countdown','data':'All done, you can relax now<br />Creating photostrip...'}))
            final_img = createStrip(base_filename, photo_strip)
            print("Final picture saved to {}".format(final_img))
            # Upload the final image
            uploadPicture('html/' + final_img)
            self.write_message(json.dumps({'type':'photo','data':final_img}))
        else:
            print("There was an error :(")
        # Might need this? still get an error when trying to do it again
        del(cam_result)

    def check_origin(self, origin):
        return(True)

class mhomeRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/index.html')

class boothRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/booth.html')


def activateCamera():
    # camera.resolution = pi_resolution
    camera.start_preview()
    return(camera)

def createStrip(base_filename, imgPaths):
    b_x, b_y = Image.open(imgPaths[0]).size
    img_ratio = b_x / b_y
    f_y = pi_resolution[1]
    f_x = int(f_y * img_ratio)
    result = Image.new("RGB", (((pi_resolution[0] * 2) + (3 * BORDERWIDTH)), ((pi_resolution[1] * 2) + (3 * BORDERWIDTH))),(255,255,255))
    for index, fPath in enumerate(imgPaths):
        tmp_img = Image.open(fPath)
        tmp_img.thumbnail((f_x, f_y), Image.ANTIALIAS)
        crop_x = (f_x - pi_resolution[0]) / 2
        # Crop image to a square
        tmp_img = tmp_img.crop((crop_x, 0, (crop_x + pi_resolution[0]), pi_resolution[1]))
        x = BORDERWIDTH + ((index % 2) * (pi_resolution[0] + BORDERWIDTH))
        y = BORDERWIDTH + ((index // 2) * (pi_resolution[1] + BORDERWIDTH))
        w, h = tmp_img.size
        result.paste(tmp_img, (x, y, x + w, y + h))
    # Open logo and get information
    logo_img = Image.open(PLOGO)
    l_x, l_y = logo_img.size
    logo_ratio = l_x / l_y
    if logo_ratio > 1.0:
        n_height = int(pi_resolution[1] / logo_ratio)
        logo_img = logo_img.resize((pi_resolution[0], n_height))
        x = BORDERWIDTH + ((PHOTOSTRIP % 2) * (pi_resolution[0] + BORDERWIDTH))
        y = BORDERWIDTH + ((PHOTOSTRIP // 2) * (pi_resolution[1] + BORDERWIDTH)) + int((pi_resolution[1] - n_height) / 2)
    else:
        n_width = int(pi_resolution[0] / logo_ratio)
        logo_img = logo_img.resize((n_width, pi_resolution[1]))
        x = BORDERWIDTH + ((PHOTOSTRIP % 2) * (pi_resolution[0] + BORDERWIDTH)) + int((pi_resolution[0] - n_width) / 2)
        y = BORDERWIDTH + ((PHOTOSTRIP // 2) * (pi_resolution[1] + BORDERWIDTH))
    w, h = logo_img.size
    result.paste(logo_img, (x, y, x + w, y + h))
    new_fpath = pic_out + base_filename + "-Final.jpg"
    result = result.resize(pi_resolution)
    result.save(new_fpath, quality=95)
    return(new_fpath.replace('html/',''))

def takePicture(cam_obj, base_filename):
    file_name = base_filename + ".jpg"
    file_path = pic_out + file_name
    sleep(1)
    cam_obj.capture(file_path)
    cam_obj.stop_preview()
    img_result = {
        'path': file_path,
        'name': file_name,
    }
    return(img_result)

def uploadPicture(picture_path):
    p = Popen([UPLOADER, "-s", "upload", picture_path, UPLOAD_DESTINATION], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output = p.communicate()[0].decode("utf-8")
    return(output)

if __name__ == "__main__":
    camera = PiCamera(resolution=pi_resolution)
    app = tornado.web.Application([
        (r'/pb-imgs/(.*)', tornado.web.StaticFileHandler, {'path': "html/pb-imgs/"}),
        (r'/', mhomeRequestHandler),
        (r'/booth', boothRequestHandler),
        (r'/ws-camera', cameraRequestHandler)
    ], static_path=getcwd())
    app.listen(l_port)
    print('*** Websocket Server Started on {} ***'.format(l_port))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("*** Websocked Server Stopped ***")
