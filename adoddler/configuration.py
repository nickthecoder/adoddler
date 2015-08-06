import os

def register_action( url, action ) :
    registered_actions[ url ] = action

port = 8000

registered_actions = dict()
base_dir = os.path.join( os.getcwd(), 'web' )
print_folder = "print"

jenv = None

printer_manager = None

gcode_snippets = []


