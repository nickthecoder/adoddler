import os
from time import sleep

from adoddler import configuration
from adoddler.action import AbstractAction

class ConnectAction( AbstractAction ) :

    def do_POST(self, handler) :

        configuration.printer_manager.connect()

        sleep(1)
        self.send_redirect( handler, "/" )


