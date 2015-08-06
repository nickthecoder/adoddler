import sys

from adoddler import configuration, settings
from adoddler.printer import *

    
pm = configuration.printer_manager

if len(sys.argv) > 1 :
    for i in range( 1, len(sys.argv) ) :
        arg = sys.argv[i]
        print "Sending file :", arg
        pm.send_filename( arg, i == len(sys.argv) - 1 )
        print "Waiting for print job to finish"
        pm.print_job.join()
        print "Print job finished"
else :
    pm.send_file( sys.stdin, True )

