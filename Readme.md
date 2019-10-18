# Pi-Photobooth

This application is based on a RaspberryPi ZeroW using a v2 PiCamera module.  The photobooth is interacted via web browser.

This application uses Python3 and Tornado python package to serve as the websocket server.

By default it will create a 3 photo strip with an added party logo.  It can be leveraged to upload to DropBox via a script written by andreafabrizi

https://github.com/andreafabrizi/Dropbox-Uploader

It is also setup to print (if enabled) to a networked printer with the option for additional prints to be made.

The main script to run is located in `src/mgp.py`  Within it there are some default values that can be modified:

