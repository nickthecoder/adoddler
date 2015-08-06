import os
from jinja2 import Environment, FileSystemLoader

from adoddler import configuration
from adoddler.action import *
from adoddler.printer import *

print "Initialising configuration"

configuration.jenv = Environment(loader=FileSystemLoader('templates'))

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
configuration.register_action( "/job", JobAction("job.html") )
configuration.register_action( "/delete", DeleteAction("delete.html") )
configuration.register_action( "/cancel", CancelAction("cancel.html") )
configuration.register_action( "/changeSettingAjax", ChangeSettingAjaxAction() )

# Comment these out if you don't have a camera
configuration.register_action( "/camera", HTMLTemplateAction("camera.html") )
configuration.register_action( "/camera.jpg", MPlayerCameraAction() )


for filename in os.listdir("gcode") :
    if filename.endswith(".gcode") :
        configuration.gcode_snippets.append( filename[0:-6] )
configuration.gcode_snippets.sort()

configuration.printer_manager = PrinterManager( "/dev/ttyACM?", baud_rate=9600 )

print "Done initialising configuration"

