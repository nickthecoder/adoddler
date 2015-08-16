class ExtrudeCounter :

    def __init__( self ) :
        self.count = 0
        self.relative = True
        self.previous = 0

    def parse( self, line ) :
        parts = line.split()
        if len( parts ) == 0 :
            return
        command = parts[0]


        # Absolute mode
        if command == "M82" or command == "G90" :
            self.relative = False
            print "Absolute"

        # Relative mode
        if command == "M83" or command == "G91" :
            self.relative = True
            print "Relative"
    
        # Reset counter
        if command == "G92" :
            e = self.parseE( parts )
            if e is not None :
                self.previous = e
                print "Reset to ", e

        # Look for the various "GOTOs" G1..G4
        if command.startswith( "G" ) :
            commandNumber = parts[0][1:]
            if commandNumber in ["1","2","3","4"] :
                
                e = self.parseE( parts )    
                if e is not None :

                    if self.relative :
                        self.count += e
                        print "Adding A ", e, self.count

                    else :
                        self.count += e - self.previous
                        print "Adding B ", e - self.previous, self.count
                        self.previous = e

    # Look for an "E" value within the parts array
    def parseE( self, parts ) :
        try :
            for i in range( 1, len( parts) ) :
                part = parts[i]
                if part.startswith( "E" ) :

                    return float(part[1:])
        except :
            pass

        return None


