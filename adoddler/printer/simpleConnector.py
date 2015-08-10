# Connects to Serial port using a single port and baud_rate.
# On linix/bsd/macos etc, then nixConnector is more flexible.

class SimpleConnector() :

    def __init__( self, device, baud_rate ) :
        self.device = devices
        self.baud_rate = baud_rate

    def connect( self ) :
        print "Connecting to", self.device, "@", self.baud_rate, "Hz"
        return Serial( self.device, self.baud_rate, timeout = 1 )        


