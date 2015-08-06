import os

from adoddler import configuration
from adoddler.action import AbstractAction

class DisconnectAction( AbstractAction ) :

    def do_POST(self, handler) :

        configuration.printer_manager.disconnect()

        self.send_redirect( handler, "/" )


