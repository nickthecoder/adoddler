import os
import socket

from jinja2 import Environment, FileSystemLoader

from adoddler import configuration
from adoddler.action import *
from adoddler.printer import *

print "Initialising configuration"

configuration.name = socket.gethostname()

configuration.jenv = Environment(loader=FileSystemLoader('templates'))
configuration.cache_templates = False

configuration.register_action( "/", IdleAction("index.html") )

configuration.print_folder = "print"

configuration.register_action( "/gcode", GCodeAction() )
configuration.register_action( "/gcodeAjax", GCodeAjaxAction() )
configuration.register_action( "/disconnect", DisconnectAction() )
configuration.register_action( "/connect", ConnectAction() )
configuration.register_action( "/settings", SettingsAction("settings.html") )
configuration.register_action( "/about", HTMLTemplateAction("about.html") )
configuration.register_action( "/folder", FolderAction("folder.html") )
configuration.register_action( "/print", PrintAction("print.html") )
configuration.register_action( "/delete", DeleteAction("delete.html") )
configuration.register_action( "/cancel", CancelAction("cancel.html") )
configuration.register_action( "/changeSettingAjax", ChangeSettingAjaxAction() )
configuration.register_action( "/error", HTMLTemplateAction('error.html') )

# Comment these out if you don't have a camera
try :
    from adoddler.action.piCameraAction import PiCameraAction
    configuration.register_action( "/camera.jpg", PiCameraAction() )
    configuration.register_action( "/camera", HTMLTemplateAction("camera.html") )
except Exception as e :
    print "Couldn't initialise PiCamera. Skipping.", e


for filename in os.listdir("gcode") :
    if filename.endswith(".gcode") :
        configuration.gcode_snippets.append( filename[0:-6] )
configuration.gcode_snippets.sort()

connector = NixConnector( ["/dev/ttyUSB?", "/dev/ttyACM?"], 115200 )
# connector = SimpleConnector( "YOUR_DEVICE", YOUR_BAUD_RATE )

configuration.printer_manager = PrinterManager( connector )

print "Done initialising configuration"

