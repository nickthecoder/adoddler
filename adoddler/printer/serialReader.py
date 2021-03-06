import sys
import traceback

from time import sleep
from threading import Thread

from adoddler import configuration

class SerialReader( Thread ) :
    """
    Reads the output from the printer.
    Counts the "ok"s
    """

    def __init__( self, connection ) :
        Thread.__init__( self )
        self.connection = connection
        self.stopping = False
        self.listeners = []

    def run( self ) :
        try :
            while not self.stopping :
                
                line = self.connection.readline()
                if line :
                    self.process_line( line )
        except Exception as e :
            pm = configuration.printer_manager
            if pm.serial_reader == self :
                pm.job_error( e )

    def process_line( self, line ) :
        stripped = line.strip( '\0' ).strip()
        print ">>", stripped

        for listener in self.listeners :
            try :
                listener( stripped )
            except :
                print(traceback.format_exc())

    def stop( self ) :
        self.stopping = True

    def add_listener( self, listener ) :
        self.listeners.append( listener )
        print "Added listener", len( self.listeners )

    def remove_listener( self, listener ) :
        if listener in self.listeners :
            self.listeners.remove( listener )
        print "Removed listener", len( self.listeners )

