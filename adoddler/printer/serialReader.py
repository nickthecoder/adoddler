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
        self.ok_count = 0
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

        if stripped.startswith( 'ok' ) :
            self.ok_count += 1
            print "## SR ok count", self.ok_count

        for listener in self.listeners :
            listener( stripped )

    def stop( self ) :
        self.stopping = True

    def add_listener( self, listener ) :
        self.listeners.append( listener )

    def remove_listener( self, listener ) :
        self.listeners.remove( listener )

