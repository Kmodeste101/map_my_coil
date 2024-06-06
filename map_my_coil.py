#!/usr/bin/python3
"""
Created on Tue Oct 17 15:27:41 2023
@author: amalajaison
"""

# Import the necessary libraries
from linact import Carrier
import numpy as np
# import threading
import time
import signal
import sys
import math
from math import sqrt
import matplotlib.pyplot as plt
# import asyncio

# labjack import
from labjack import ljm

from arduino_current_controller_routines import *

# Set up the mapper robot

# Create a carrier object
carrier=Carrier()
# initialize the carrier
carrier.initialize()


# Set up the labjack to read out the fluxgate magnetometer

# open a connection to the labjack and set the ranges for measurement
# LabJack T7 Pro connection settings
handle=ljm.openS("T7","ANY","ANY")
# SCU channel configuration
scu_channels=[0,1,2] # Change to the appropriate SCU channels for X,
                     # Y, and Z axes

# Configure SCU channels as analog inputs
for channel in scu_channels:
    ljm.eWriteName(handle,"AIN%s_RANGE"%channel,10.0)  # Sets the
                                                       # range to +/-
                                                       # 10V


# Open a connection to the Arduino, so that we can set currents on the
# coils.
cc=acc()


coil_sign=[1]*50 # initialize all coil signs to 1

# coils you want to set to -1
coils_to_set_negative = [9,10,12,14,17,27,30,32,33,34,35,
                         43,44,45,46,47,49,24,25,26,
                         41,42,36,37,0,1,5,4,6,8]

# change sign of coils to -1
for coil in coils_to_set_negative:
    coil_sign[coil] = -1


# Prepare a data file to write results to
data_file_name="voltage_data.txt"
with open(data_file_name, "w") as data_file:
     data_file.write("Position (X, Y, Z) | Voltages (X, Y, Z)\n")

# List of positions where we would like to measure the magnetic field
positions=np.mgrid[-25:26:1,0:1:1,0:1:1].reshape(3,-1).T
print(positions)
#quit()

# Set up a signal handler that gracefully exits if Ctrl-C is pressed
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    time.sleep(10)
    carrier.shutdown()
    ljm.close(handle)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Tell the current controller to set all the voltages

def set_all_voltages():
    with open('current.csv','r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                try:
                    coil,current=map(float,line.strip().split(","))
                    coil=int(coil)
                    current=float(current)
                    if coil<0 or coil>49:
                        print("Invalid coil %d"%(coil))
                    else:
                        print("Setting coil %2d %10.6f with sign %3d"%(coil,current,coil_sign[coil]))
                        cc.set_current(coil,current*coil_sign[coil])
                except ValueError:
                    print("Error parsing line:", line)
    #write_eeprom()

set_all_voltages()


x_data = []
y_data = []
z_data = []
for position in positions:
    # move to that [x,y,z] position
    for i in range(3):
        carrier.move_to(float(position[i]),i)
    # wait until we are in position
    in_position=False
    while(not in_position):
        xnow=carrier.get_position(0)
        ynow=carrier.get_position(1)
        znow=carrier.get_position(2)
        if sqrt((position[0]-xnow)**2+(position[1]-ynow)**2+(position[2]-znow)**2)<.001:
            in_position=True
    time.sleep(1)
    
    # turn on the coil
    cc.turn_on()
    time.sleep(0.3)
    
    # make a measurement of the magnetic field

    voltages_on=[ljm.eReadName(handle,"AIN%s"%channel) for channel in scu_channels]
    nT_on=[voltages_on[i]*100/10*1000 for i in range(len(voltages_on))]

    # turn off the coil
    cc.turn_neg()
    # make a measurement of the magnetic field
    time.sleep(0.3)
    voltages_off=[ljm.eReadName(handle,"AIN%s"%channel) for channel in scu_channels]
    nT_off=[voltages_off[i]*100/10*1000 for i in range(len(voltages_on))]

    voltages_delta=[voltages_on[i]-voltages_off[i] for i in range(len(voltages_on))]
    nT_delta=[(nT_on[i]-nT_off[i])/2 for i in range(len(voltages_on))]
    x_data.append(nT_delta[0])
    y_data.append(nT_delta[1])
    z_data.append(nT_delta[2])
    # Print out the measurement and the current position
    print(f"Position: {position}, Magnetic Field Measurements (X, Y, Z): {nT_delta}")

    with open(data_file_name, "a") as data_file:  # Open the file in append mode
         data_file.write(f"{position} | {nT_delta}\n")

    cc.turn_off()


plt.figure(figsize=(12, 6))
plt.plot(range(len(positions)), x_data, label="X-axis")
plt.plot(range(len(positions)), y_data, label="Y-axis")
plt.plot(range(len(positions)), z_data, label="Z-axis")

plt.xlabel("Position")
plt.ylabel("Magnetic Field (nT)")
plt.title("Magnetic Field Measurements")
plt.legend()

carrier.shutdown()
ljm.close(handle)

plt.show()

