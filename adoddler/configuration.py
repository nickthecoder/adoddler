import os

def register_action( url, action ) :
    registered_actions[ url ] = action

port = 8000

name = "adoddler"

registered_actions = dict()
base_dir = os.path.join( os.getcwd(), 'web' )
print_folder = "print"

jenv = None
cache_templates = False

printer_manager = None

gcode_snippets = []


