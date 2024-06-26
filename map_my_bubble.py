#!/usr/bin/python3

# Import the necessary libraries
import PySimpleGUI as sg
from linact import Carrier
import time
# import threading
import time
# import asyncio


# Create a carrier object
carrier = Carrier()
# initialize the carrier
carrier.initialize()

#positions=[[0,0,0],
#           [0,0,1],
#           [5,0,0],
#           [0,2,0]
#]

import numpy as np
import math
from math import sqrt
positions=np.mgrid[0:11:1,0:11:1,0:11:1].reshape(3,-1).T
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



def total_distance(ps):
    
    d = 0
    for x in range(len(ps)-1):
        p1=ps[x]
        p2=ps[x+1]

        x1=p1[0]
        y1=p1[1]
        z1=p1[2]

        x2=p2[0]
        y2=p2[1]
        z2=p2[2]

        distance= math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
        d += distance

    return d


print('The total distance initially was',total_distance(positions))


from random import randint

nswaps=0
for i in range(10000):
    # calculate total distance
    d1=total_distance(positions)
    # pick any two random positions
    r1=randint(0,len(positions)-1)
    r2=randint(0,len(positions)-1)
    # try a swap
    positions[[r1,r2]]=positions[[r2,r1]]
    # calculate the total distance again
    d2=total_distance(positions)
    if (d2>d1):
        # if it got worse, swap them back again
        positions[[r1,r2]]=positions[[r2,r1]]
    else:
        nswaps+=1
        print('Swap successful at position',r1,r2)

print('The total distance after',nswaps,'swaps was',total_distance(positions))

        
import signal
import sys
from math import sqrt

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    carrier.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print('Doing ',len(positions),' positions')

     

print('This will take',total_distance(positions),' seconds')

print(positions)
stop()

last_position=positions[0]
for position in positions:
    # move to that [x,y,z] position
    for i in range(3):
        carrier.move_to(float(position[i]), i)
    # wait for a time equal to the distance moved in cm
    sleep_for=sqrt((position[0]-last_position[0])**2+(position[1]-last_position[1])**2+(position[2]-last_position[2])**2)
    time.sleep(sleep_for)
    # make a measurement of the magnetic field

    # on to the next position!
    last_position=position

carrier.shutdown()
