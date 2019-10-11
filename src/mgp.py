#!/usr/bin/env python3

"""
DESCRIPTION
A Python socket server to act as a backend service for 
Raspberrypi ZeroW web based photobooth.

"""
__author__ = 'Rob Martin'
__version__ = 0.2

# import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import json
from os import getcwd
from PIL import Image, ImageFont, ImageDraw
from picamera import PiCamera
from time import sleep
from datetime import datetime, timedelta

l_port = 8888
# pi_resolution = (3280, 2464)
pic_out = "html/pb-imgs/"
PHOTOSTRIP = 4
FINALWIDTH = 400
BORDERWIDTH = 10
PMESSAGE = "Finley's 2 Wild Birthday Party!\n10/19/2019"

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
            final_img = createStrip(base_filename, photo_strip)
            print("Final picture saved to {}".format(final_img))
            # print("Pictures saved to\npb-imgs/{}".format("\npb-imgs/".join(photo_strip)))
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
    f_x = FINALWIDTH
    f_y = int(f_x / img_ratio)
    result = Image.new("RGB", ((f_x + (2 * BORDERWIDTH)), (50 + (f_y * PHOTOSTRIP) + ((PHOTOSTRIP + 1) * BORDERWIDTH))))
    for index, fPath in enumerate(imgPaths):
        tmp_img = Image.open(fPath)
        tmp_img.thumbnail((f_x, f_y), Image.ANTIALIAS)
        x = BORDERWIDTH
        y = index * f_y + ((index + 1) * BORDERWIDTH)
        w, h = tmp_img.size
        result.paste(tmp_img, (x, y, x + w, y + h))
    # Try adding text
    tmp_draw = ImageDraw.Draw(result)
    font = ImageFont.truetype(getcwd() + "/fonts/Verdana.ttf", 24)
    tmp_draw.text((BORDERWIDTH, ((f_y * PHOTOSTRIP) + (PHOTOSTRIP * BORDERWIDTH))), PMESSAGE, (255,0,255), font=font)
    new_fpath = pic_out + base_filename + "-Final.jpg"
    result.save(new_fpath)
    return(new_fpath.replace('html/',''))

def takePicture(cam_obj, base_filename):
    file_name = base_filename + ".jpg"
    file_path = pic_out + file_name
    cam_obj.capture(file_path)
    cam_obj.stop_preview()
    img_result = {
        'path': file_path,
        'name': file_name,
    }
    return(img_result)

if __name__ == "__main__":
    camera = PiCamera()
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
