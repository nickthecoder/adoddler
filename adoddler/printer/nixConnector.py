# Connects to Serial port using Unix style files (in /dev)
# Windows users may want to use "SimpleConnector", or write something
# appropriate themselves.

import os
import serial

class NixConnector() :

    def __init__( self, devices, baud_rate ) :
        """
        devices is either a single string, or a list of strings.
        If it ends with a '?', then it will be replaced by digits 0..9.
        """
        self.devices = devices
        self.baud_rate = baud_rate

    def connect( self ) :
        result = None

        if isinstance( self.devices, basestring) :
            result = self.__connect( device )
        else :
            for device in self.devices :
                result = self.__connect( device )
                if result :
                    break

        if result :
            return result

        raise Exception( "Failed to open device(s) : " + str(self.devices) )

    def __connect( self, device ) :
        
        dev = self.__find_device( device )
        if dev :
            print "Connecting to", dev, "@", self.baud_rate, "Hz"
            return serial.Serial( dev, self.baud_rate, timeout = 1 )        
        return None

    def __find_device( self, device ) :

        if device.endswith( "?" ) :    
            for i in range( 0,10 ) :
                dev = device[0:-1] + str( i )
                if os.path.exists( dev ) :
                    return dev
        else :

            if os.path.exists( device ) :
                return self.device

        return None

