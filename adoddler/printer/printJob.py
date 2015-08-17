from time import sleep
from threading import Thread

from adoddler import configuration
from adoddler.printer import JobStatus, PrinterStatus, ExtrudeCounter

class PrintJob( Thread ) :
    """
    Sends gcode to the printer.
    """

    def __init__( self, fileOrPath, auto_disconnect = False ) :

        Thread.__init__( self )
        self.status = JobStatus.CREATED
        self.input = None
        self.auto_disconnect = auto_disconnect

        # Note, command_total is NOT set when sending from a filename
        self.command_total = None
        self.command_count = 0

        # Note, extrude_total is NOT set when sending from a filename
        self.extrude_total = None
        self.extrude_counter = None

        if type( fileOrPath ) == str :
            print "*** GCode file :", fileOrPath
            self.input = open(fileOrPath, "r")

            # Count the number of commands and measure filament
            self.command_total = 0
            self.extrude_total = 0
            extrude_counter = ExtrudeCounter()

            for line in self.input :
                line = self.tidy( line )
                if line :
                    self.command_total += 1
            
                    extrude_counter.parse( line )
            self.extrude_total = extrude_counter.count
            self.input.seek(0)

        else :
            self.input = fileOrPath

    def send( self ) :

        pm = configuration.printer_manager
        pm.ensure_idle()

        if pm.status == PrinterStatus.IDLE :

            print "*** Setting to active and print job"
            pm.status = PrinterStatus.ACTIVE
            pm.print_job = self
            self.status = JobStatus.RUNNING
            print "*** start thread"
            self.start()
        
    def cancel( self ) :
        if self.status == JobStatus.RUNNING :
            self.status = JobStatus.CANCELLING
            print "## Print job status now CANCELLING"

    def run( self ) :
        print "***** Job started"

        try :
            pm = configuration.printer_manager
            self.serial_reader = pm.serial_reader;
            self.serial_reader.ok_count = 0
            output = pm.connection
            self.command_count = 0
            self.extrude_counter = ExtrudeCounter()

            for line in self.input :

                # Let's not get too far ahead of ourselves!
                while self.command_count - self.serial_reader.ok_count > 10 :
                    if self.status == JobStatus.CANCELLING :
                        break
                    sleep( 0.1 )

                if  self.status == JobStatus.CANCELLING :
                    print "## Breaking out of the loop due to CANCELLING"
                    break

                line = self.tidy( line )
                if line :
                    print "<<", line
                    output.write( line )
                    output.write( "\n" )
                    self.command_count += 1        
                    self.extrude_counter.parse( line )

        except Exception as e :
            pm.errors.append( str( e ) )
            self.cancel()
            self.auto_disconnect = True

        self.__end()

    def __end( self ) :

        pm = configuration.printer_manager
        self.input.close()
        print "## Closed the input file"

        while self.__running() :
            print "## PrintJob sleeping until oks tally", self.status == JobStatus.CANCELLING, self.command_count, self.serial_reader.ok_count
            sleep(1)

        print "*** ending job"
        pm.status = PrinterStatus.IDLE
        pm.print_job = None
        self.status = JobStatus.ENDED

        if self.auto_disconnect :
            self.serial_reader.stop()
            pm.disconnect()

        print "***** Job finished"

    def __running( self ) :
        if self.status == JobStatus.CANCELLING :
            return False

        return self.command_count > self.serial_reader.ok_count

    def tidy( self, line ) :
        semi = line.find( ";" )
        if semi >= 0 :
            line = line[0:semi]
        return line.strip()

