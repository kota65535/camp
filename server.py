#!/usr/bin/env python
"""
Creates an HTTP server with basic auth and websocket communication.
"""
import argparse
import base64
import os
import io

import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
import picamera

# Hashed password for comparison and a cookie for login cache
ROOT = os.path.normpath(os.path.dirname(__file__))

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", port=args.port)


class ErrorHandler(tornado.web.RequestHandler):
    def get(self):
        self.send_error(status_code=403)


class WebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""

        # Start an infinite loop when this is called
        if message == "read_camera":
            self.camera_loop = PeriodicCallback(self.loop, 10)
            self.camera_loop.start()

        # Extensibility for other methods
        else:
            print("Unsupported function: " + message)

    def loop(self):
        """Sends camera images in an infinite loop."""
        sio = io.BytesIO()
        camera.capture(sio, "jpeg", use_video_port=True)

        try:
            self.write_message(base64.b64encode(sio.getvalue()))
        except tornado.websocket.WebSocketClosedError:
            self.camera_loop.stop()


parser = argparse.ArgumentParser(description="Starts a webserver that connects to a webcam.")
parser.add_argument("--port", type=int, default=8000, help="The port on which to serve the website.")
parser.add_argument("--resolution", type=str, default="640,480", help="The video resolution which is represented by width and height, joined by comma.")
args = parser.parse_args()

try:
    width, height = [int(n) for n in args.resolution.split(',')]
except:
    raise Exception("Invalid resolution format: %s" % args.resolution)

camera = picamera.PiCamera()
camera.resolution = (width, height)
camera.start_preview()

handlers = [(r"/", IndexHandler),
            (r"/websocket", WebSocket),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': ROOT})]
application = tornado.web.Application(handlers)
application.listen(args.port)

tornado.ioloop.IOLoop.instance().start()
