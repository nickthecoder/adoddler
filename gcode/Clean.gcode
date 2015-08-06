G28 Z0     ;move Z to min endstops
G1 Z15.0 F2400 ;move the head up 15mm
G92 E0         ;zero the extruded length
G1 F200 E10    ;extrude Xmm
G92 E0         ;zero the extruded length again

