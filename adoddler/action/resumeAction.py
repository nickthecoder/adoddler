import os
from time import sleep

from adoddler import configuration
from adoddler.action import AbstractAction
from adoddler.printer import PrinterStatus

class ResumeAction( AbstractAction ) :

    def do_POST( self, handler ) :
        
        pm = configuration.printer_manager
        if pm.status == PrinterStatus.PAUSED :
            pm.resume()

        self.send_redirect( handler, "/" )

