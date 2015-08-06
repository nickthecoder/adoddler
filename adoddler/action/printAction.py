import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class PrintAction( HTMLTemplateAction ) :

    def do_POST( self, handler ) :
        
        if 'print' in handler.parameters :
            file = handler.parameters['print'][0]

            path = os.path.join( configuration.print_folder, file + ".gcode" )
            configuration.printer_manager.send_filename( path )

            self.send_redirect( handler, "/job" )

        else :

            self.send_redirect( handler, "/folder" )

