import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class PrintAction( HTMLTemplateAction ) :

    def do_POST( self, handler ) :
        
        if 'file' in handler.parameters :
            file = handler.parameters['file'][0]

            if file.find("..") >= 0 :
                self.error( handler, "Invalid filename (contains '..')" )
                return

            path = os.path.join( configuration.print_folder, file + ".gcode" )
            configuration.printer_manager.send( path, file )

            self.send_redirect( handler, "/" )

        else :

            self.send_redirect( handler, "/folder" )

