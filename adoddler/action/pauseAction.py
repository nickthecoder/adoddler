import os
from time import sleep

from adoddler import configuration
from adoddler.action import AbstractAction
from adoddler.printer import PrinterStatus

class PauseAction( AbstractAction ) :

    def do_POST( self, handler ) :
        
        pm = configuration.printer_manager
        if pm.status == PrinterStatus.ACTIVE :
            pm.pause()

        self.send_redirect( handler, "/" )

