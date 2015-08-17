import os

from adoddler import configuration
from adoddler.action import HTMLTemplateAction

class SettingsAction( HTMLTemplateAction ) :

    def data_GET(self, handler) :

        pm = configuration.printer_manager
        pm.ensure_connected()
    
        # handler instance is created for each request, therefore, we can use it to
        # store the results of the M501 command (we can't store the results here,
        printer_settings = []

        listener = lambda line : self.process_line( printer_settings, line )

        # We listen for the results, (to parse the output), but print_manager can ignore it
        pm.serial_reader.add_listener( listener )
        pm.serial_reader.remove_listener( pm.listener )

        # Run the "settings" command
        pm.send( os.path.join( os.path.join( "gcode", "misc", ), "settings.gcode" ) )

        # Wait for the job to end, and stop listening
        print "SettingsAction joining print job"
        pm.print_job.join()
        print "SettingsAction print job complete"
        pm.serial_reader.remove_listener( listener )
        pm.serial_reader.add_listener( pm.listener )

        # Now we can display the results
        return {'printer_settings': printer_settings }


    def process_line( self, printer_settings, line ) :
        if line == 'ok' :
            return

        if line.startswith( "echo:" ) :
            line = line[5:]
            if line.startswith( "  " ) :
                line = line[2:]
                values = line.split()
                d = printer_settings[len(printer_settings)-1]
                d['code'] = values[0]
                d['fields'] = []
                for i in range( 1, len( values ) ) :
                    letter = values[i][0]
                    value = float( values[i][1:] )
                    d['fields'].append( {'letter': letter, 'value': value } )

            else :
                if line.endswith( ":" ) :
                    printer_settings.append( {'name':line[0:-1]} )

        
