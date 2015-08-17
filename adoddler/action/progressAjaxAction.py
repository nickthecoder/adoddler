import os
import StringIO

from time import sleep

from adoddler import configuration
from adoddler.action import AbstractAction
from adoddler.printer import PrinterStatus

class ProgressAjaxAction( AbstractAction ) :

    def get_content_type( self, handler ) :
        return "text/plain"

    def do_POST(self, handler) :
        self.do_GET( handler )

    def do_GET(self, handler) :

        pm = configuration.printer_manager
        job = pm.print_job

        if job is None :
            handler.wfile.write( "done done" )
        else :
            handler.wfile.write( str( job.extrude_counter.count ) )
            handler.wfile.write( " " )
            handler.wfile.write( str( job.extrude_total ) )

        handler.wfile.write( " " )
        handler.wfile.write( str( pm.temperature ) )

        if pm.status == PrinterStatus.IDLE :
            path = os.path.join( os.path.join( "gcode", "misc", ), "idle.gcode" )
            pm.send( path )
            
