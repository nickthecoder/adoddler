# Connects to Serial port using Unix style files (in /dev)
# Windows users may want to use "SimpleConnector", or write something
# appropriate themselves.

class SimpleConnector() :

    def __init__( self, device, baud_rate ) :
        self.device = devices
        self.baud_rate = baud_rate

    def connect( self ) :
        print "Connecting to", self.device, "@", self.baud_rate, "Hz"
        return Serial( self.device, self.baud_rate, timeout = 1 )        


