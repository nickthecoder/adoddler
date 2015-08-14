import os
from time import sleep

from adoddler.printer import SerialReader, PrintJob, PrinterStatus

class PrinterManager :


    def __init__( self, connector ) :
        self.connector = connector

        self.status = PrinterStatus.DISCONNECTED

        self.print_job = None
        self.serial_reader = None
        self.temperature = None
        self.messages = []
        self.warnings = []
        self.errors = []


    def clear_messages( self ) :
        self.messages = []
        self.warnings = []
        self.errors = []


    def ensure_connected( self ) :
        if self.status == PrinterStatus.DISCONNECTED :
            self.connect()

    def ensure_idle( self ) :
        self.ensure_connected()
        if self.status != PrinterStatus.IDLE :
            raise Exception( "Printer is not IDLE" )


    def connect( self ) :
        if self.status == PrinterStatus.DISCONNECTED :

            
            self.status = PrinterStatus.CONNECTING
            self.connection = self.connector.connect()
            self.serial_reader = SerialReader( self.connection )
            self.serial_reader.start()
            
            self.listener = lambda line : self.process_line( line )
            self.serial_reader.add_listener( self.listener )

            self.status = PrinterStatus.IDLE

    def process_line( self, line ) :
        if line == "start" and self.status == PrinterStatus.CONNECTING :
            self.status = PrinterStatus.IDLE

        if line.startswith( "T:" ) :
            parts = line.split( " " )
            bits = parts[0].split( ":" )
            self.temperature = float( bits[1] )
        elif line.startswith( "ok T:" ) :
            parts = line.split( " " )
            bits = parts[1].split( ":" )
            self.temperature = float( bits[1] )
        elif line.startswith( "echo: " ) :
            self.warnings.append( line[6:] )


    def disconnect( self ) :

        self.status = PrinterStatus.PENDING

        self.temperature = None

        if self.print_job :
            self.print_job.cancel()
            # Wait up to 5 seconds for the print job to cancel
            for a in range( 0, 5 ) :
                sleep(1)
                if self.status == PrinterStatus.IDLE :
                    break

        if self.serial_reader :
            self.serial_reader.remove_listener( self.listener )
            self.serial_reader.stop()
            self.serial_reader = None

        if self.connection :
            self.connection.close()
            self.connection = None

        self.status = PrinterStatus.DISCONNECTED


    def send_file( self, f, auto_disconnect = False ) :
        self.ensure_connected()

        if self.status == PrinterStatus.IDLE :
            PrintJob().send_file( f, auto_disconnect )
        else :
            raise Exception( "Printer not idle" )

    def send_filename( self, path, auto_disconnect = False ) :
        self.ensure_connected()

        if self.status == PrinterStatus.IDLE :
            PrintJob().send_filename( path, auto_disconnect )
        else :
            raise Exception( "Printer not idle" )

    def cancel( self ) :
        if self.print_job :
            print "## Cancelling job"
            self.print_job.cancel()

    def job_error( self, e ) :
        self.errors.append( str(e) )
        self.cancel()


