import os
from subprocess import call

import SimpleHTTPServer

from adoddler import configuration
from adoddler.action import AbstractAction

class MPlayerCameraAction( AbstractAction ) :

    def do_GET(self, handler) :
        # Take three images, as the first two are often/alwats corrupt, the third is good!
        call( ["mplayer", "--msglevel=all=-1", "-vo", "jpeg", "-frames", "3", "tv://" ] )
        call( ["rm", "00000001.jpg" ] )
        call( ["rm", "00000002.jpg" ] )
        call( ["mv", "00000003.jpg", os.path.join( "web", "camera.jpg" ) ] )

        # Use the default handler to send the image.
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(handler)

