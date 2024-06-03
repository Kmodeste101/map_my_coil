#!/usr/bin/env python3
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

# Create a carrier object
carrier = Carrier()
# initialize the carrier
carrier.initialize()

# open a connection to the labjack and set the ranges for measurement
# LabJack T7 Pro connection settings
handle=ljm.openS("T7", "ANY", "ANY")  # Change if needed
# SCU channel configuration
scu_channels = [0, 1, 2]  # Change to the appropriate SCU channels for X, Y, and Z axes

# Configure SCU channels as analog inputs
for channel in scu_channels:
    ljm.eWriteName(handle, "AIN%s_RANGE" % channel, 10.0)  # Sets the range to +/- 10V



# open a connection to the Arduino, so that we can set currents on the coils.
import serial
ser=serial.Serial('/dev/ttyACM0', 9600)

data_file_name="voltage_data.txt"
with open(data_file_name, "w") as data_file:
     data_file.write("Position (X, Y, Z) | Voltages (X, Y, Z)\n")

     



#positions=[[0,0,0],
#           [0,0,1],
#           [5,0,0],
#           [0,2,0]
#]

#positions=np.mgrid[0:11:1,0:11:1,0:11:1].reshape(3,-1).T
positions=np.mgrid[0:11:1,0:1:1,0:1:1].reshape(3,-1).T

total_distance = 0
last_position = positions[0]

position=positions[1]

print('The shape of positions is ',np.shape(positions))
print('The zeroth shape of positions is ',np.shape(positions)[0])
print('The length of positions is ',len(positions))


print(positions)
print('The first entry in the positions array is ',positions[0])
print('The second entry in the positions array is ',positions[1])
print('Something is ',positions[2][1])
last_position=[0,0,0]
p1= positions[0]
p2= positions[1]

x1=p1[0]
y1=p1[1]
z1=p1[2]

x2=p2[0]
y2=p2[1]
z2=p2[2]

print(z1)
print(y2)

distance= math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)  
print (distance)

some_position=positions[1]
print('some_position is',some_position)
print('something is',some_position[2])

print('start of our for loop')
i=0
i_end=10

#################################################
sum=0
for x in range(11):
    sum=sum+x
print(sum)

#################################################
total_distance = 0
for x in range(len(positions)-1):
    # first time through the loop, x=0
    # second time through the loop, x=1
    # ...
    # last time through the loop, x=2
    print('x = ',x)
    print(positions[x])
    print(positions[x+1])
    p1=positions[x]
    p2=positions[x+1]

    x1=p1[0]
    y1=p1[1]
    z1=p1[2]

    x2=p2[0]
    y2=p2[1]
    z2=p2[2]

    distance= math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
    print(distance)
    total_distance += distance

    print(total_distance)
    
# in C++, we would write
#for(i=0;i<11;i++){
#        }
#stop()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    time.sleep(10)
    carrier.shutdown()
    ljm.close(handle)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print('Doing ',len(positions),' positions')
print('This will take',total_distance,' seconds')


def set_coil_current(cs,chans,volts):
    # clear Arduino buffer
    ser.reset_input_buffer()
    stuff = ser.read_all()
    print('stuff',stuff.decode())

    for chan, volt in zip(chans, volts):
    # write instruction to Arduino
     set_voltage=str(volts)
     set_channel=str(chan)
     set_cs=str(cs)
    ser.write(('<SET '+set_cs+' '+set_channel+' '+set_voltage+'>\n').encode())
    time.sleep(.1)
    with open(data_file_name, "a") as data_file:
        data_file.write(f"{position} | {volts}\n")

    
    # read and print response from Arduino
    line=ser.read_all()
    print('line',line.decode())
    

def write_arduino_mux(cs,chan):
    # clear Arduino buffer
    for i in range(10):
        time.sleep(.1)
        stuff=ser.read_all()
        print('stuff',i,stuff.decode())
    # write instruction to Arduino
    set_channel=str(chan)
    set_cs=str(cs)
    ser.write(('<MUX '+set_cs+' '+set_channel+'>\n').encode())
    time.sleep(.1)
    # read and print response from Arduino
    line=ser.read_all()
    print('line',line.decode())
    # clear Arduino buffer
    for i in range(10):
        time.sleep(.1)
        stuff=ser.read_all()
        print('stuff',i,stuff.decode())

    
print('Sleep before MUX')
time.sleep(1)
write_arduino_mux(8,6)

last_position=positions[0]
x_data = []
y_data = []
z_data = []
for position in positions:
    # move to that [x,y,z] position
    for i in range(3):
        carrier.move_to(float(position[i]), i)
    # wait for a time equal to the distance moved in cm
    sleep_for=sqrt((position[0]-last_position[0])**2+(position[1]-last_position[1])**2+(position[2]-last_position[2])**2)
    time.sleep(sleep_for)

    # turn on the coil
    set_coil_current(9, [8,5,4,11,1,2,14], [5.0,5.0,5.0,5.0,5.0,5.0,5.0])
    time.sleep(0.5)
    # Open the file for writing
    

  
    
    # make a measurement of the magnetic field

    voltages_on=[ljm.eReadName(handle, "AIN%s" % channel) for channel in scu_channels]
    nT_on=[voltages_on[i]*100/10*1000 for i in range(len(voltages_on))]
    time.sleep(0.5)

    # turn off the coil
    
    set_coil_current(8, [8,5,4,11,1,2,14], [0.0,0.0,0.0,0.0,0.0,0.0,0.0])
    # make a measurement of the magnetic field
    time.sleep(0.5)
    voltages_off = [ljm.eReadName(handle, "AIN%s" % channel) for channel in scu_channels]
    time.sleep(0.5)
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

plt.show()

carrier.shutdown()
ljm.close(handle)
