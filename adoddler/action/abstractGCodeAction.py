import os

from adoddler import configuration
from adoddler.action import AbstractAction

class AbstractGCodeAction( AbstractAction ) :

    def do_POST(self, handler) :

        names = handler.parameters.get("gcode")
        if not names :
            self.error( handler, "Parameter 'gcode' is missing" )
        

        name = names[0]

        if name.find("..") >= 0 :
            self.error( handler, "Invalid gcode name (contains '..')" )
            return

        short = handler.parameters.get("short") is not None
        path = os.path.join( "gcode", name + ".gcode" )
        print "@@GCode Action", path, "short?", short, handler.parameters.get("short")
        configuration.printer_manager.send( path, name, is_short=short )

        # Child classes will do more after this.


