import os
import picamera.PiCamera:

import SimpleHTTPServer

from adoddler import configuration
from adoddler.action import AbstractAction

class PiCameraAction( AbstractAction ) :

    def do_GET(self, handler) :

        try :
            ensure_camera()

            camera.capture('/web/camera.jpg')
        except Exception as e :
            print "Failed to take a photo : ", e
            self.camera = None

        # Use the default handler to send the image.
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(handler)

    def ensure_camera() :
        if self.camera = None :
            self.camera = PiCamera( resolution=(640,480) )
            camera.start_preview()
            # Camera warm-up time
            time.sleep(2)

