from time import sleep
from threading import Thread

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
        while not self.stopping :
            
            line = self.connection.readline()
            if line :
                self.process_line( line )
    
    def process_line( self, line ) :
        line = line.strip()
        if line.startswith( 'ok' ):
            self.ok_count += 1
        print ">", line

        for listener in self.listeners :
            listener( line )

    def stop( self ) :
        self.stopping = True

    def add_listener( self, listener ) :
        self.listeners.append( listener )

    def remove_listener( self, listener ) :
        self.listeners.remove( listener )

