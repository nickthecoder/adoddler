import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class FolderAction( HTMLTemplateAction ) :

    def data_GET( self, handler ) :

        files = []
        for filename in os.listdir( configuration.print_folder ) :
            if filename.endswith(".gcode") :
                files.append( filename[0:-6] )

        files.sort()
        return { 'files': files }

