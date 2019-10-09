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
from picamera import PiCamera
from time import sleep
from datetime import datetime, timedelta

l_port = 8888
# pi_resolution = (3280, 2464)
pic_out = "html/pb-imgs/"

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
        count_down = 3
        picam = activateCamera()
        while count_down > 0:
            self.write_message(json.dumps({'type':'countdown','data':count_down}))
            sleep(1)
            count_down -= 1
        self.write_message(json.dumps({'type':'countdown','data':'Cheese!'}))
        cam_result = takePicture(picam)
        if cam_result:
            print("Picture saved to {}".format(cam_result[0]))
            self.write_message(json.dumps({'type':'photo','data':cam_result[1]}))
        else:
            print("There was an error :(")
        # Might need this? still get an error when trying to do it again
        del(cam_result)
 
    def check_origin(self, origin):
        return True 
    
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

def takePicture(cam_obj):
    # try:
    file_name = getDATETIME() + ".jpg"
    file_path = pic_out + file_name
    cam_obj.capture(file_path)
    cam_obj.stop_preview()
    return([file_path,file_name])
    # except:
    #     return(False)

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
