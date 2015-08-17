import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction
from adoddler.printer import PrinterStatus

class IdleAction( HTMLTemplateAction ) :

    def do_GET(self, handler) :
        pm = configuration.printer_manager

        HTMLTemplateAction.do_GET( self, handler )

        pm.clear_messages()

        if pm.status == PrinterStatus.IDLE :
            path = os.path.join( os.path.join( "gcode", "misc", ), "idle.gcode" )
            pm.send( path, is_short=True )


