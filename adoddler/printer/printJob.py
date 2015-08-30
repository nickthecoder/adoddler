from time import sleep
from threading import Thread

from adoddler import configuration
from adoddler.printer import JobStatus, PrinterStatus, ExtrudeCounter

class PrintJob( Thread ) :
    """
    Sends gcode to the printer.
    """

    def __init__( self, fileOrPath, is_short=False ) :

        Thread.__init__( self )
        self.status = JobStatus.CREATED
        self.input = None
        self.is_short = is_short
        self.paused = False
        self.paused_short_job = None # A job which can be popped off the queue while this is paused.
        self.ok_count = 0

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

        self.status = JobStatus.RUNNING
        print "*** start thread"
        self.start()
        
    def cancel( self ) :
        if self.paused_short_job is not None :
            self.paused_short_job.cancel()

        if self.status == JobStatus.RUNNING :
            self.status = JobStatus.CANCELLING
            self.paused = False
            print "## Print job status now CANCELLING"


    def pause( self ) :
        print "~~~~~~~~~~~ Pausing ~~~~~~~~~~~~"
        self.paused = True
        self.__tally_oks() # Wait for existing command(s) to finish
        self.serial_reader.remove_listener( self.listen )
        self.paused_relative = self.extrude_counter.relative
        self.paused_position = None

        print "~~~ Paused ish"

        self.serial_reader.add_listener( self.parse_position )
        self.send_command( "M114", True ) # Get current position.
        self.serial_reader.remove_listener( self.parse_position )
        print "~~~Pos", self.paused_position
        print "~~~Relative?", self.paused_relative


    def resume( self ) :
        self.send_command( "G90" ) # Absolute positioning
        if self.paused_position is not None :
            x = self.paused_position[0]
            y = self.paused_position[1]
            z = self.paused_position[2]
            if x is not None and y is not None and z is not None :
                self.send_command( "G0 X" + str(x) + " Y" + str(y) + " Z" + str(z) )

        if self.paused_relative :
            self.send_command( "G91" ) # Set to relative positioning

        # If we have manually extrudeded extra filament during pause, then set the value back,
        # so that extra filament isn't counted for the remainder of the print.
        if self.paused_position and self.paused_position[3] is not None :
            print "~~~Setting extrusion position to", self.paused_position[3]
            self.send_command( "G92 E" + str( self.paused_position[3] ) )

        self.serial_reader.add_listener( self.listen )
        self.paused = False


    def send_command( self, command, wait=True ) :
        print "Sending command", command, wait
        configuration.printer_manager.connection.write( command + "\n" )
        self.command_count += 1        
        if wait :
            self.__tally_oks()
        print"Sent command", command


    def parse_position( self, line ) :
        print "~~~Pause parsing line", line
        if line.startswith( "X:") :
            x = None
            y = None
            z = None
            e = None
            parts = line.split(" ")
            print "Parts", parts
            for part in parts :
                subs = part.split( ":" )
                print "Subs", subs
                if subs[0] == 'X' and x is None :
                    x = float( subs[1] )
                if subs[0] == 'Y' and y is None :
                    y = float( subs[1] )
                if subs[0] == 'Z' and z is None :
                    z = float( subs[1] )
                if subs[0] == 'E' and e is None :
                    e = float( subs[1] )
            self.paused_position = ( x, y, z, e )
            print "~~~Pause found position", self.paused_position
        print "End parse_position"


    def listen( self, line ) :
        if line.startswith( 'ok' ) :
            self.ok_count += 1
            print "## Job LISTEN ok count", self.ok_count, "vs", self.command_count

        

    def run( self ) :
        print "***** Job started"

        try :
            pm = configuration.printer_manager
            self.serial_reader = pm.serial_reader;
            self.ok_count = 0
            self.serial_reader.add_listener( self.listen )
            output = pm.connection
            self.command_count = 0
            self.extrude_counter = ExtrudeCounter()

            for line in self.input :

                # Let's not get too far ahead of ourselves!
                while self.command_count - self.ok_count > 1 : # MORE Allow more than 1??
                    while self.paused :
                        if self.paused_short_job is None :
                            self.paused_short_job = pm.pop_job()
                            if self.paused_short_job :
                                print "~~~Sending short job while paused"
                                self.paused_short_job.send()
                        else :
                            if self.paused_short_job.status == JobStatus.ENDED :
                                self.paused_short_job = None
                        sleep( 1 );

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

            while self.paused :
                sleep( 1 );

        except Exception as e :
            pm.errors.append( str( e ) )
            self.cancel()

        self.__end()


    def __tally_oks( self ) :

        while self.__running() :
            print "## PrintJob sleeping until oks tally", self.status == JobStatus.CANCELLING, self.command_count, self.ok_count
            sleep(1)


    def __end( self ) :

        pm = configuration.printer_manager
        self.input.close()
        print "## Closed the input file"

        self.__tally_oks()

        print "*** ending job"
        self.status = JobStatus.ENDED
        pm.job_ended( self )
        print "***** Job finished"

    def __running( self ) :
        if self.status == JobStatus.CANCELLING :
            return False

        return self.command_count > self.ok_count

    def tidy( self, line ) :
        semi = line.find( ";" )
        if semi >= 0 :
            line = line[0:semi]
        return line.strip()

