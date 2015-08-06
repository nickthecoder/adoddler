import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class DeleteAction( HTMLTemplateAction ) :

    def do_POST( self, handler ) :
        
        if 'delete' in handler.parameters :
            file = handler.parameters['delete'][0]

            path = os.path.join( configuration.print_folder, file + ".gcode" )
            os.remove( path )

        self.send_redirect( handler, "/folder" )

