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
from picamera import PiCamera, PiRenderer
from time import sleep
from datetime import datetime, timedelta

l_port = 8888
pi_resolution: (3280, 2464)
pic_out = "pb-imges/"

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
        count_down = 5
        while count_down > 0:
            self.write_message(json.dumps({'type':'countdown','data':count_down}))
            sleep(1)
            count_down -= 1
        self.write_message(json.dumps({'type':'countdown','data':'Cheese!'}))
 
    def check_origin(self, origin):
        return True 
    
class mhomeRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/index.html')

class boothRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/booth.html')


def activateCamera():
    camera = PiCamera()
    camera.resolution = pi_resolution
    camera.start_preview()
    return(camera)



if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/', mhomeRequestHandler),
        (r'/booth', boothRequestHandler),
        (r'/ws-camera', cameraRequestHandler)
    ], static_path="/home/pi/Scripts")
    app.listen(l_port)
    print('*** Websocket Server Started on {} ***'.format(l_port))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("*** Websocked Server Stopped ***")
