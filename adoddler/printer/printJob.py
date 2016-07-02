from time import sleep
from threading import Thread

from adoddler import configuration
from adoddler.printer import JobStatus, PrinterStatus, ExtrudeCounter

class PrintJob( Thread ) :
    """
    Sends gcode to the printer.
    """

    def __init__( self, fileOrPath, name, is_short=False ) :

        Thread.__init__( self )
        self.name = name
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

        # Remember if the job was using relative or absolute positioning. During pause we will move relative, and
        # will need to revert back when we resume.
        # BUG. We aren't remembering the units (and onPause.gcode sets to metric).
        self.paused_relative = self.extrude_counter.relative

        # Note, this is stopping the MAIN listener, which will be added again when we resume.
        self.serial_reader.remove_listener( self.listen )

        print "~~~ Paused ish"

        self.paused_position = None
        self.serial_reader.add_listener( self.parse_position )
        # Note, this listener is removed in parse_position

        self.send_command( "M114", expect_ok=False ) # Get current position.


    def resume( self ) :
        
        # The main listener was removed in the pause method, so add it back
        self.serial_reader.add_listener( self.listen )
        
        self.send_command( "G90" ) # Absolute positioning
        print "Now using absolute positioning"
        
        if self.paused_position is not None :
            x = self.paused_position[0]
            y = self.paused_position[1]
            z = self.paused_position[2]
            print "Paused position : ", x, y, z
            if x is not None and y is not None and z is not None :
                self.send_command( "G0 X" + str(x) + " Y" + str(y) + " Z" + str(z) )
                print "Reset print head position"

        # Make doubly sure that the listener added by the pause method is remove
        # It should have removed itself when it parsed the position.
        self.serial_reader.remove_listener( self.parse_position )

        if self.paused_relative :
            print "Reset to absolute positioning"
            self.send_command( "G91" ) # Set to relative positioning

        # BUG. If the job was not using metric units, we need to switch back, as onPause.gcode sets to metric.

        # If we have manually extruded extra filament during pause, then set the value back,
        # so that extra filament isn't counted for the remainder of the print.
        if self.paused_position and self.paused_position[3] is not None :
            print "~~~Setting extrusion position to", self.paused_position[3]
            self.send_command( "G92 E" + str( self.paused_position[3] ) )
            print "Reset extrude counter"

        print "Resume complete"
        self.paused = False


    def send_command( self, command, wait=True, expect_ok=True ) :
        print "Sending command", command, wait
        configuration.printer_manager.connection.write( command + "\n" )
        self.command_count += 1        
        if wait :
            self.__tally_oks()
        print"Sent command", command


    def parse_position( self, line ) :
        print "parse_position line :", line
        if line.startswith( "X:") :
            x = None
            y = None
            z = None
            e = None
            parts = line.split(" ")
            for part in parts :
                subs = part.split( ":" )
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

            # We have found what we need, now we can remove ourselves
            self.serial_reader.remove_listener( self.parse_position )


    def listen( self, line ) :
        print "PJ L:isten", self.name, ". Heard :", line
        if line.startswith( 'ok' ) :
            self.ok_count += 1
            print "## Job", self.name, "LISTEN ok count", self.ok_count, "of", self.command_count

        

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
                while self.command_count - self.ok_count > 4 :
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
            print "## PrintJob", self.name, "sleeping until oks tally", self.ok_count, "of", self.command_count
            sleep(1)


    def __end( self ) :
        self.__tally_oks()

        self.serial_reader.remove_listener( self.listen )
        self.serial_reader.remove_listener( self.parse_position )
        pm = configuration.printer_manager
        self.input.close()
        print "##", self.name, "Closed the input file"

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

