import os

from adoddler import configuration
from adoddler.action import AbstractAction

class AbstractGCodeAction( AbstractAction ) :

    def do_POST(self, handler) :

        snippets = handler.parameters["gcode"]
        if not snippets :
            self.error( handler, "Parameter 'gcode' is missing" )

        snippet = snippets[0]

        if snippet.find("..") >= 0 :
            self.error( handler, "Invalid gcode name (contains '..')" )
            return

        path = os.path.join( "gcode", snippet + ".gcode" )
        configuration.printer_manager.send( path )

        # Child classes will do more after this.


