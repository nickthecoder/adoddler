import os

from adoddler import configuration
from adoddler.action import AbstractAction

class ConnectAction( AbstractAction ) :

    def do_POST(self, handler) :

        configuration.printer_manager.connect()

        self.send_redirect( handler, "/" )


