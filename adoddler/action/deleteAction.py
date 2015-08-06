import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class DeleteAction( HTMLTemplateAction ) :

    def do_POST( self, handler ) :
        
        if 'file' in handler.parameters :
            file = handler.parameters['file'][0]

            if file.find("..") >= 0 :
                self.error( handler, "Invalid filename (contains '..')" )
                return

            path = os.path.join( configuration.print_folder, file + ".gcode" )
            os.remove( path )

        self.send_redirect( handler, "/folder" )

