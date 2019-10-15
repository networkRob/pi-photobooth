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
import base64
import io
import json
from random import choice
from os import getcwd
from subprocess import Popen, PIPE
from PIL import Image
from picamera import PiCamera
from time import sleep
from datetime import datetime, timedelta

# Party Specific globals
PLOGO = "imgs/fin-logo.jpg"
MSGINSTRUCT = "Welcome to the photobooth.  There will be a series of {} photos taken.  Don't forget to have fun and stay silly!"
MSGSNAP = "Cheese!"
MSGLEFT = 'Here we go again!<br />{} more to go...'
MSGREADY = ["Smile!", "Make a SILLY Face!", "Show your inner ANIMAL"]
MSGDONE = 'All done, you can relax now<br />Creating photostrip...'
MSGRANDOM = ["Awesome!","Oh, How Cute...", "ROARRRR!", "That's a keeper", "The Monkeys are on the loose!"]

# Camera Specifics
l_port = 8888
pi_resolution = (1200, 1800)
pi_thumbnail = (600, 900)

# Global Utilities
PRINTERNAME = 'Canon_SELPHY_CP1300-1'
PRINTENABLED = False
pic_out = "html/pb-imgs/"
UPLOADER = "./dropbox_uploader.sh"
UPLOAD_DESTINATION = "mTest/"
LASTPRINTED = ''
# Number of photos to take
PHOTOSTRIP = 3
BORDERWIDTH = 10

def getDATETIME():
    return(datetime.now().strftime("%Y%m%d-%H%M%S"))

class cameraRequestHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("New connection from: {}".format(self.request.remote_ip))
        self.write_message({'type':'hello','data':"hello user"})

    def on_message(self,message):
        print("[{0}] Sent: {1}".format(self.request.remote_ip,message))
        recv_msg = json.loads(message)
        if recv_msg['type'] == 'hello':
            self.write_message({
                'type': 'hello',
                'data': MSGINSTRUCT.format(PHOTOSTRIP)
            })
            sleep(5)
            self.countdown()
        elif recv_msg['type'] == 'print':
            print('Printer requested: {}'.format(recv_msg))
            if LASTPRINTED:
                printImage(int(recv_msg['data']),LASTPRINTED)

    def countdown(self):
        global LASTPRINTED
        photo_strip = []
        pIND = 0
        self.write_message({
            'type': 'ready',
            'data': MSGREADY[pIND]
        })
        picam = activateCamera()
        sleep(3)
        base_filename = getDATETIME()
        while pIND < PHOTOSTRIP:
            count_down = 3
            while count_down > 0:
                self.write_message({
                    'type':'countdown',
                    'data':count_down
                })
                sleep(1)
                count_down -= 1
            self.write_message({
                'type':'countdown',
                'data': MSGSNAP
            })
            cam_result = takePicture(picam,base_filename + "-{}".format(pIND + 1))
            self.write_message({
                'type':'update',
                'data':{
                    'msg': choice(MSGRANDOM),
                    'imgData': bencode64(cam_result['path'])
                }})
            # Upload photo to Dropbox App
            uploadPicture(cam_result['path'])
            photo_strip.append(cam_result['path'])
            print("Pictures saved to pb-imgs/{}".format(cam_result['name']))
            pIND += 1
            if pIND < PHOTOSTRIP:
                self.write_message({
                    'type': 'ready',
                    'data': MSGLEFT.format(PHOTOSTRIP - pIND)
                })
                sleep(4)
                self.write_message({
                    'type': 'ready',
                    'data': MSGREADY[pIND]
                })
                sleep(5)
        if photo_strip:
            self.write_message({
                'type':'done',
                'data': MSGDONE
            })
            final_img = createStrip(base_filename, photo_strip)
            print("Final picture saved to {}".format(final_img))
            printImage(1, 'html/{}'.format(final_img))
            LASTPRINTED = 'html/{}'.format(final_img)
            # Upload the final image
            uploadPicture('html/' + final_img)
            self.write_message({
                'type':'photo',
                'data':final_img
            })
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

def bencode64(filePath):
    tmp_buff = io.BytesIO()
    img = Image.open(filePath)
    img = img.resize(pi_thumbnail)
    img.save(tmp_buff, format="JPEG")
    tmp_buff.seek(0)
    imgData = base64.b64encode(tmp_buff.read())
    imgData = imgData.decode('utf-8')
    return(imgData)

def activateCamera():
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

def printImage(copies, picture_path):
    copy_string = '{} copy'.format(copies) if copies == 1 else '{} copies'.format(copies)
    print("Printing {0} of {1}".format(copy_string, picture_path))
    if PRINTENABLED:
        print('Sending to {}'.format(PRINTERNAME))
        p = Popen(["lp", "-n", copies, "-d", PRINTERNAME, picture_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output = p.communicate()[0].decode("utf-8")
        return(output)
    else:
        print("Printing to {} is currently disabled".format(PRINTERNAME))

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
