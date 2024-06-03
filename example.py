#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 12:36:10 2023

@author: amalajaison
"""
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt

# Load channel and current values from the file
with open('channel_current_values.txt', 'r') as file:
    lines = file.readlines()

# Extract channel and current values
channels, current = zip(*(map(float, line.strip().split(',')) for line in lines))

# max and min current values
cmax = max(current)
cmin = min(current)

# number of currents
nc = len(channels)
xpos = np.arange(nc)
my_cmap = plt.cm.get_cmap('bwr')
bank = ['A', 'B', 'C', 'D']
bars = [bank[int(x/16)] + str(x % 16) for x in xpos]

# plot function
def plot():
    data_color = [(x - cmin) / (cmax - cmin) for x in current]
    colors = my_cmap(data_color)

    # plotting the graph
    ax.clear()
    ax.bar(xpos, current, color=colors)
    # Create names on the x-axis
    ax.set_xticks(xpos)
    ax.set_xticklabels(bars, rotation=90, ha='center', va='top')
    ax.set_ylim([cmin, cmax])
    ax.set_ylabel('current (mA)')
    canvas.draw()

# main Tkinter window
window = Tk()

# setting the title
window.title('Current control')

# dimensions of the main window
window.geometry("1000x500")
topframe = Frame(window)
topframe.pack(side=TOP)

# button that displays the plot
plot_button = Button(topframe, command=plot, height=2, width=8, text="Plot", bg='blue', fg='white')
plot_button.pack(side=TOP)

# the figure that will contain the plot
fig = Figure(dpi=100)
fig.set_tight_layout(True)

# adding the subplot
ax = fig.add_subplot(111)

# creating the Tkinter canvas containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=window)

# plot it once
plot()

# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack(side=BOTTOM, fill='x')

# run the gui
window.mainloop()
