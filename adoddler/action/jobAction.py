import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class JobAction( HTMLTemplateAction ) :

     def data_GET(self, handler) :

        pm = configuration.printer_manager
        pm.clear_messages()

        return { 'job': pm.print_job }

