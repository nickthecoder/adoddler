import os
from subprocess import call

import SimpleHTTPServer

from adoddler import configuration
from adoddler.action import AbstractAction

class UVCCaptureCameraAction( AbstractAction ) :

    def do_GET(self, handler) :
        call( ["uvccapture", "-m", "-x640", "-y480", "-oweb/camera.jpg"] )

        # Use the default handler to send the image.
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(handler)

