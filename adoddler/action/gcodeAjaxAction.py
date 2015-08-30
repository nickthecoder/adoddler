import os
import traceback

from time import sleep

from adoddler import configuration
from adoddler.action import AbstractGCodeAction

class GCodeAjaxAction( AbstractGCodeAction ) :

    def get_content_type( self, handler ) :
        return "text/plain"

    def do_POST(self, handler) :

        try :
            AbstractGCodeAction.do_POST( self, handler )

            sleep( 0.2 );

            for message in configuration.printer_manager.messages :
                handler.wfile.write( message + "\n" )

            for message in configuration.printer_manager.warnings :
                handler.wfile.write( message + "\n")

            for message in configuration.printer_manager.errors :
                handler.wfile.write( message + "\n")

            configuration.printer_manager.clear_messages()
        
        except Exception as e :
            handler.wfile.write( "Failed : " + str( e ) )
            print(traceback.format_exc())
    
