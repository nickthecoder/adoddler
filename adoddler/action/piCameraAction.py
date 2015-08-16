import os
import time
import traceback

from picamera import PiCamera

import SimpleHTTPServer

from adoddler import configuration
from adoddler.action import AbstractAction

class PiCameraAction( AbstractAction ) :

    def __init__( self ) :
        #AbstractAction.__init__(self)
        self.camera = None

    def do_GET(self, handler) :

        try :
            self.ensure_camera()
            self.camera.capture('web/camera.jpg')

        except Exception as e :
            print "Failed to take a photo"
            print(traceback.format_exc())
            self.camera = None

        # Use the default handler to send the image.
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(handler)

    def ensure_camera( self ) :
        if self.camera:
            return

        self.camera = PiCamera( resolution=(640,480) )
        self.camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
