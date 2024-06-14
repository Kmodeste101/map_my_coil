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

# load theoretical fields

data=np.transpose(np.loadtxt('xscan.out'))
x_sim,bx_sim,by_sim,bz_sim=data
bx_sim=bx_sim*1e9 # convert to nT
by_sim=by_sim*1e9
bz_sim=bz_sim*1e9


data=np.transpose(np.loadtxt('xscan_target.out'))
x_target,bx_target,by_target,bz_target=data
bx_target=bx_target*1e9 # convert to nT
by_target=by_target*1e9
bz_target=bz_target*1e9

# load metadata about the theoretical fields
import json
with open('data.json') as json_file:
    graphdata=json.load(json_file)

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
# coils.  This uses the acc "Arduino Current Controller" class.
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
data_file_name="voltage_data_%d_%d.txt"%(graphdata["l"],graphdata["m"])
with open(data_file_name, "w") as data_file:
     data_file.write("xmapper (cm), ymapper (cm), zmapper (cm), Bx_fg (nT), By_fg (nT), Bz_fg (nT)\n")

# List of positions where we would like to measure the magnetic field
positions=np.mgrid[-25:26:1,0:1:1,0:1:1].reshape(3,-1).T
print(positions)

# Set up a signal handler that gracefully exits if Ctrl-C is pressed
def signal_handler(sig,frame):
    print('You pressed Ctrl+C!')
    time.sleep(10)
    carrier.shutdown()
    ljm.close(handle)
    sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)

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

fg_gain=1
fg_settle=0.3 # seconds
robo_wobble=0.1 # seconds

x_data=[]
y_data=[]
z_data=[]
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
    time.sleep(robo_wobble) # sleeping time to stop the wobbling
    
    # turn on the coil
    cc.turn_on()
    time.sleep(fg_settle)
    
    # make a measurement of the magnetic field

    voltages_on=[ljm.eReadName(handle,"AIN%s"%channel) for channel in scu_channels]
    print("raw voltages_on",voltages_on)
    nT_on=[voltages_on[i]*100/10*1000/fg_gain for i in range(len(voltages_on))]

    # turn neg the coil
    cc.turn_neg()
    # make a measurement of the magnetic field
    time.sleep(fg_settle)
    voltages_off=[ljm.eReadName(handle,"AIN%s"%channel) for channel in scu_channels]
    nT_off=[voltages_off[i]*100/10*1000/fg_gain for i in range(len(voltages_on))]

    voltages_delta=[voltages_on[i]-voltages_off[i] for i in range(len(voltages_on))]
    nT_delta=[(nT_on[i]-nT_off[i])/2 for i in range(len(voltages_on))] # divide by two because subtracting neg from pos
    x_data.append(nT_delta[0])
    y_data.append(nT_delta[1])
    z_data.append(nT_delta[2])
    # Print out the measurement and the current position
    print(f"Position: {position}, Magnetic Field Measurements (X, Y, Z): {nT_delta}")

    with open(data_file_name, "a") as data_file:  # Open the file in append mode
         data_file.write(f"{position[0]} {position[1]} {position[2]} {nT_delta[0]} {nT_delta[1]} {nT_delta[2]}\n")

    cc.turn_off()

# used to test graphing
#x_data=range(len(positions))
#y_data=range(len(positions))
#z_data=range(len(positions))
x_data=np.array(x_data)
y_data=np.array(y_data)
z_data=np.array(z_data)


# fix measurement axes to be as in simulation

# position:
# The scan direction is the minus x direction in simulation

# fluxgate measurement:

# The fluxgate z-axis is aligned with the minus x direction in simulation.

# The fluxgate y-axis is aligned with the minus z direction in simulation.

# According to the right-hand rule, the fluxgate x-axis is aligned
# with the plus y direction in simulation.

plt.figure()
plt.scatter(-positions[:,0]*.01,-z_data,color="b",label="$B_x(x,0,0)$ meas",marker='.')
plt.scatter(-positions[:,0]*.01,-x_data,color="r",label="$B_y(x,0,0)$ meas",marker='.')
plt.scatter(-positions[:,0]*.01,y_data,color="g",label="$B_z(x,0,0)$ meas",marker='.')

# now plot simulation on top of this
plt.plot(x_sim,bx_sim,color="b",label="$B_x(x,0,0)$ sim")
plt.plot(x_sim,by_sim,color="r",label="$B_y(x,0,0)$ sim")
plt.plot(x_sim,bz_sim,color="g",label="$B_z(x,0,0)$ sim")


plt.plot(x_target,bx_target,'--',color="b",label="$B_x(x,0,0)=%s$"%(graphdata['Pix']))
plt.plot(x_target,by_target,'--',color="r",label="$B_y(x,0,0)=%s$"%(graphdata['Piy']))
plt.plot(x_target,bz_target,'--',color="g",label="$B_z(x,0,0)=%s$"%(graphdata['Piz']))

plt.xlabel("Position along $x$-axis (cm)")
plt.ylabel("Magnetic Field (nT)")



ax=plt.gca()
h,l=ax.get_legend_handles_labels()
ph=[plt.plot([],marker="", ls="")[0]]*3
#handles=[ph[0]]+h[::3]+[ph[1]]+h[1::3]+[ph[2]]+h[2::3]
#labels=["Title 1:"]+l[::3]+["Title 2:"]+l[1::3]+["Title 3:"]+l[2::3]
handles=[ph[0]]+h[0:3]+[ph[1]]+h[3:6]+[ph[2]]+h[6:9]
labels=[r'\underline{Measured}']+l[0:3]+[r"\underline{Simulated}"]+l[3:6]+[r"\underline{Target} $(\ell,m)=(%d,%d)$"%(graphdata['l'],graphdata['m'])]+l[6:9]

plt.rc('text',usetex=True)
plt.xlabel("Position along $x$-axis (cm)")
plt.ylabel("Magnetic Field (nT)")
plt.legend(handles, labels, ncol=3)

carrier.shutdown()
ljm.close(handle)

plt.savefig("/home/jmartin/Desktop/delete_later/field_measurements_%d_%d.png"%(graphdata['l'],graphdata['m']),dpi=300,bbox_inches='tight')

plt.show()

