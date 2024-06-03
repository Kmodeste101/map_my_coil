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
import serial
import matplotlib.pyplot as plt
# import asyncio

# labjack import
from labjack import ljm

import re

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
import serial
ser=serial.Serial('/dev/ttyACM0',115200)

# Set up a list of coil signs, determined by using the GUI and a
# fluxgate to determine the sign
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
positions=np.mgrid[0:11:1,0:1:1,0:1:1].reshape(3,-1).T
print(positions)


# Set up a signal handler that gracefully exits if Ctrl-C is pressed
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    time.sleep(10)
    carrier.shutdown()
    ljm.close(handle)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def CheckReadUntil(readUntil):
    outputCharacters = ""
    while True:
        ch = ser.read().decode()
        if len(ch) == 0:
            break
        outputCharacters += ch
        if outputCharacters[-len(readUntil):] == readUntil:
            break
    outputLines = ''.join(outputCharacters)
    return outputLines

def set_voltage(i,voltage):
    ser.write(f'<STV {i} {voltage}>\n'.encode())
    line=CheckReadUntil("V\r\n")
    m=re.search("Voltage (\d+) set to ([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?) V",line)
    i_readback=int(m.group(1))
    voltage_readback=float(m.group(2))
    print(f"Arduino confirms voltage for i {i_readback} is {voltage_readback}")

def set_current(i,current):
    ser.write(f'<STC {i} {current}>\n'.encode())
    line=CheckReadUntil("A\r\n")
    m=re.search("Current (\d+) set to ([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?) A",line)
    i_readback=int(m.group(1))
    current_readback=float(m.group(2))
    print(f"Arduino confirms current for i {i_readback} is {current_readback}")

def write_eeprom():
    ser.write(f'<WRI>'.encode())
    line=CheckReadUntil(".\r\n")
    print(line)

def turn_on():
    ser.write(f'<ONA>'.encode())
    line=CheckReadUntil(".\r\n")
    print(line)

def turn_off():
    ser.write(f'<OFA>'.encode())
    line=CheckReadUntil(".\r\n")
    print(line)

def turn_neg():
    ser.write(f'<ONN>'.encode())
    line=CheckReadUntil(".\r\n")
    print(line)

def zero_all_voltages():
    ser.write(f'<ZERO>\n'.encode())
    line = CheckReadUntil(ser, "Done zeroing.\r\n")
    print(line)
    if 'Done zeroing.' in line:
        print("All voltages set to zero")
    else:
        print("Failed to set all voltages to zero")

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
                        print("Setting coil %2d %10.6f"%(coil,current))
                        set_current(coil,current)
                except ValueError:
                    print("Error parsing line:", line)
    #write_eeprom()


first_read=CheckReadUntil("voltage>\r\n")
print(first_read)


set_all_voltages()


last_position=positions[0]
x_data = []
y_data = []
z_data = []
for position in positions:
    # move to that [x,y,z] position
    for i in range(3):
        carrier.move_to(float(position[i]),i)
    # wait for a time equal to the distance moved in cm
    sleep_for=sqrt((position[0]-last_position[0])**2+(position[1]-last_position[1])**2+(position[2]-last_position[2])**2)
    time.sleep(sleep_for)

    # turn on the coil
    turn_on()
    time.sleep(0.5)
    
    # make a measurement of the magnetic field

    voltages_on=[ljm.eReadName(handle,"AIN%s"%channel) for channel in scu_channels]
    nT_on=[voltages_on[i]*100/10*1000 for i in range(len(voltages_on))]

    # turn off the coil
    turn_off()
    # make a measurement of the magnetic field
    time.sleep(0.5)
    voltages_off=[ljm.eReadName(handle,"AIN%s"%channel) for channel in scu_channels]
    nT_off=[voltages_off[i]*100/10*1000 for i in range(len(voltages_on))]

    voltages_delta=[voltages_on[i]-voltages_off[i] for i in range(len(voltages_on))]
    nT_delta=[nT_on[i]-nT_off[i] for i in range(len(voltages_on))]
    x_data.append(nT_delta[0])
    y_data.append(nT_delta[1])
    z_data.append(nT_delta[2])
   
    # Print out the measurement and the current position
    print(f"Position: {position}, Magnetic Field Measurements (X, Y, Z): {nT_delta}")

    with open(data_file_name, "a") as data_file:  # Open the file in append mode
         data_file.write(f"{position} | {nT_delta}\n")


    # on to the next position!
    last_position=position


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
