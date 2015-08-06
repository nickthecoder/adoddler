import os

from adoddler import configuration
from adoddler.action import AbstractGCodeAction

class GCodeAction( AbstractGCodeAction ) :

    def do_POST(self, handler) :
        AbstractGCodeAction.do_POST( self, handler )

        self.send_redirect( handler, "/" )


