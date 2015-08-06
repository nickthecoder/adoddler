import os
import StringIO

from time import sleep

from adoddler import configuration
from adoddler.action import AbstractAction

class ChangeSettingAjaxAction( AbstractAction ) :

    def get_content_type( self, handler ) :
        return "text/plain"

    def do_POST(self, handler) :

        code = handler.parameters['code'][0]
        letter = handler.parameters['letter'][0]
        value = handler.parameters['value'][0]

        command = code + " " + letter + value + "\nM500\n"

        # print "Change setting with the following gcode :\n", command
        f = StringIO.StringIO( command )
        configuration.printer_manager.send_file( f )

        handler.wfile.write( value )

