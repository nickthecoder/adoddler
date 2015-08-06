from time import sleep
from threading import Thread

from adoddler import configuration
from adoddler.printer import JobStatus, PrinterStatus

class PrintJob( Thread ) :
    """
    Sends gcode to the printer.
    """

    def __init__( self ) :
        Thread.__init__( self )
        self.status = JobStatus.CREATED
        self.input = None
        self.auto_disconnect = False

    def send_filename( self, path, auto_disconnect = False ) :
        self.send_file( open(path, "r"), auto_disconnect )
 

    def send_file( self, f, auto_disconnect = False ) :
        self.auto_disconnect = auto_disconnect
        self.input = f
        pm = configuration.printer_manager

        pm.ensure_idle()

        if pm.status == PrinterStatus.IDLE :
    
            self.status = JobStatus.RUNNING
            self.start()
        
    def cancel( self ) :
        if self.status == JobStatus.RUNNING :
            self.status = JobStatus.CANCELLING

    def run( self ) :
        print "***** Job started"

        pm = configuration.printer_manager
        self.serial_reader = pm.serial_reader;
        self.serial_reader.ok_count = 0
        output = pm.connection
        self.command_count = 0

        for line in self.input :
            if  self.status == JobStatus.CANCELLING :
                break
            line = self.tidy( line )
            if line :
                output.write( line )
                output.write( "\n" )
                self.command_count += 1        

        self.input.close()

        while self.__running() :
            sleep(1)

        pm.status = PrinterStatus.IDLE
        pm.print_job = None
        self.status = JobStatus.ENDED

        if self.auto_disconnect :
            self.serial_reader.stop()
            pm.disconnect()

        print "***** Job finished"

    def __running( self ) :
        return self.command_count > self.serial_reader.ok_count

    def tidy( self, line ) :
        semi = line.find( ";" )
        if semi :
            line = line[0:semi]
        return line.strip()

