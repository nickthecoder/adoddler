import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class CancelAction( HTMLTemplateAction ) :

    def do_POST( self, handler ) :
        
        job = configuration.printer_manager.print_job
        if job :
            job.cancel()

        self.send_redirect( handler, "/index" )

