import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class PrintAction( HTMLTemplateAction ) :

    def do_POST( self, handler ) :
        
        file = handler.parameters['print'][0]

        path = os.path.join( configuration.print_folder, file + ".gcode" )
        configuration.printer_manager.send_filename( path )

        self.send_redirect( handler, "/job" )

