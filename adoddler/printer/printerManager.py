import os
from time import sleep
import datetime

from adoddler.printer import SerialReader, PrintJob, PrinterStatus

class PrinterManager :


    def __init__( self, connector ) :
        self.connector = connector

        self.status = PrinterStatus.DISCONNECTED

        self.print_job = None
        self.serial_reader = None
        self._temperature = None
        self._temperature_datetime = None
        self.messages = []
        self.warnings = []
        self.errors = []
        self.queue = []
        self.queue_only_short = True

    # Return the previous temperature reading, but if it was a while ago, then
    # ignore the stale value and return None instead.
    @property
    def temperature( self ) :
        if self._temperature_datetime is None :
            return None

        if ( datetime.datetime.now() - self._temperature_datetime ).seconds < 20 :
            return self._temperature

        return None

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

            try :
                self.status = PrinterStatus.CONNECTING
                self.connection = self.connector.connect()
            except :
                self.status = PrinterStatus.DISCONNECTED
                return

            self.serial_reader = SerialReader( self.connection )
            self.serial_reader.start()
            
            self.listener = lambda line : self.process_line( line )
            self.serial_reader.add_listener( self.listener )

            # Give the printer a time to start up
            sleep( 2 )
            self.status = PrinterStatus.IDLE

    def process_line( self, line ) :
        if line == "start" and self.status == PrinterStatus.CONNECTING :
            self.status = PrinterStatus.IDLE

        if line.startswith( "T:" ):
            parts = line.split( " " )
            bits = parts[0].split( ":" )
            self._temperature = float( bits[1] )
            self._temperature_datetime = datetime.datetime.now()
        elif line.startswith( "ok T:" ) :
            parts = line.split( " " )
            bits = parts[1].split( ":" )
            self._temperature = float( bits[1] )
            self._temperature_datetime = datetime.datetime.now()

        elif line.startswith( "echo: " ) :
            self.warnings.append( line[6:] )


    def disconnect( self ) :

        self.status = PrinterStatus.PENDING

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


    def send( self, f, name, is_short=False ) :
        self.ensure_connected()

        # Short jobs can be added to the queue for when then current job ends,
        # or is paused. This allows moving the heading during pause.
        # The paused PrintJob will take care of poping off the new PrintJob from the
        # queue and staring it.
        if is_short and self.status != PrinterStatus.IDLE :
            print "~~~Queued job"
            self.queue.append( PrintJob( f, name, is_short ) )
            return

        if self.status == PrinterStatus.IDLE :

            if self.print_job is None :
                job = PrintJob( f, name, is_short )
                job.send()
                self.print_job = job
                print "*** Setting to active"
                self.status = PrinterStatus.ACTIVE


            else :
                # We are currently processing a short job, so queue this one.
                self.queue.append( job )
                if not is_short :
                    self.queue_only_short = False
        else :
            raise Exception( "Printer not idle" )


    def pause( self ) :
        
        if self.status != PrinterStatus.ACTIVE :
            raise Exception( "Printer not idle" )

        print "PM Pausing"
        self.status = PrinterStatus.PAUSED
        self.print_job.pause()
        self.send( os.path.join( os.path.join( "gcode", "misc" ), "onPause.gcode" ), "onPause", is_short=True )


    def resume( self ) :
        if self.status != PrinterStatus.PAUSED :
            raise Exception( "Printer not paused" )

        print "PM Resuming"
        self.send( os.path.join( os.path.join( "gcode", "misc" ), "onResume.gcode" ), "onResume", is_short=True )
        self.print_job.resume()
        self.status = PrinterStatus.ACTIVE


    def job_ended( self, job ) :

        if ( job == self.print_job ) :
            self.print_job = None
            self.status = PrinterStatus.IDLE

        job = self.pop_job()
        if job :
            print "Sending a queued job"
            job.send()
            

    def pop_job( self ) :
        if len( self.queue ) > 0 :
            job = self.queue[0]
            del( self.queue[0] )
            if len( self.queue ) == 0 :
                self.queue_only_short = True
            return job
        return None

    def cancel( self ) :
        if self.print_job :
            print "## Cancelling job"
            self.print_job.cancel()

    def job_error( self, e ) :
        self.errors.append( str(e) )
        self.cancel()


