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
from picamera import PiCamera, PiRenderer
from time import sleep
from datetime import datetime, timedelta

l_port = 8888

class cameraRequestHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("New connection from: {}".format(self.request.remote_ip))
        self.write_message("hello user")
        #self.write_message(json.dumps([lo_sw.data,lo_sw.all_intfs,datetime.now().strftime("%Y-%m-%d %H:%M:%S")]))
        # self.schedule_update()
    
    def on_message(self,message):
        print("[{0}] Sent: {1}".format(self.request.remote_ip,message))        

    # def schedule_update(self):
    #     self.timeout = tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1),self.update_client)
    
    # def update_client(self):
    #     try:
    #         #self.write_message(json.dumps([lo_sw.data,lo_sw.all_intfs,datetime.now().strftime("%Y-%m-%d %H:%M:%S")]))
    #         self.write_message(json.dumps([1,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),lo_sw.data]))
    #         # sleep(30)
    #     # except:
    #     #     print("Connection closed:")
    #     finally:
    #         self.schedule_update()
 
    def on_close(self):
        print('connection closed')
        tornado.ioloop.IOLoop.instance().remove_timeout(self.timeout)
 
    def check_origin(self, origin):
        return True
    
class mhomeRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/index.html')

class boothRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/booth.html')

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
