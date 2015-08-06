import os
from jinja2 import Environment, FileSystemLoader

from adoddler import configuration
from adoddler.action import *
from adoddler.printer import *

print "Initialising configuration"

configuration.jenv = Environment(loader=FileSystemLoader('templates'))

configuration.register_action( "/", IdleAction("index.html") )

configuration.register_action( "/gcode", GCodeAction() )
configuration.register_action( "/gcodeAjax", GCodeAjaxAction() )
configuration.register_action( "/disconnect", DisconnectAction() )
configuration.register_action( "/connect", ConnectAction() )
configuration.register_action( "/settings", SettingsAction("settings.html") )
configuration.register_action( "/about", HTMLTemplateAction("about.html") )

configuration.register_action( "/camera", HTMLTemplateAction("camera.html") )
configuration.register_action( "/camera.jpg", MPlayerCameraAction() )

for i in range( 0,10 ) :
    device = "/dev/ttyACM" + str( i )
    if os.path.exists( device ) :
        configuration.printer_manager = PrinterManager( device, baud_rate=9600 )

if configuration.printer_manager is None :
    raise Exception( "Failed to find printer device file /dev/ttyACM0" )

for filename in os.listdir("gcode") :
    if filename.endswith(".gcode") :
        configuration.gcode_snippets.append( filename[0:-6] )
configuration.gcode_snippets.sort()


print "Done initialising configuration"

