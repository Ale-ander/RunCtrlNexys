#!/usr/bin/python3

import numpy as np
import math
import serial
import time
import sys

#from math import sin, sqrt
try:
    #ser = serial.Serial("/dev/ttyS0", 115200, timeout= 0.2)
    ser = serial.Serial("COM6", 115200, timeout= 0.2)
    print("connected to: " + ser.portstr)
    
except:
    print(" Seriale non TROVATA ")
    quit()

ser.writelines(b"ss sdsdd  sassd")
ser.flushOutput()
time_A = int(time.time())
time_R =  time_A

while True:
    time_A = int(time.time())
    
    if time_A != time_R :
        time_R = time_A
       	
        ser.write(b'9 f\n\r')
        print ("Tempo >" , time_R )
        
    
    bytesToRead = ser.inWaiting()   
    ser.read(bytesToRead)
    #ser.read()

ser.close()       