"""
Creaated on 2023-02-21
@author: Tung Ki Wong
@description: This file is used to create a GUI for the Field Mapper control using PySimpleGUI
"""

# Import the necessary libraries
import PySimpleGUI as sg
from linact import Carrier
# import threading
# import time
# import asyncio


# Create a carrier object
carrier = Carrier()
# initialize the carrier
carrier.initialize()

# Use the theme for the GUI
sg.theme('DarkAmber')

# Create a frame for current position
frame_layout0 = [   [sg.Text('Move x-axis'), sg.InputText(key = "-Move_X-" ,size=(10, 1)), sg.Button('Move-x')], 
                    [sg.Text('Move y-axis'), sg.InputText(key = "-Move_Y-" ,size=(10, 1)), sg.Button('Move-y')],
                    [sg.Text('Move z-axis'), sg.InputText(key = "-Move_Z-" ,size=(10, 1)), sg.Button('Move-z')],
                    [sg.Checkbox('Non safe mode', default = False, key = "-Non_safe_mode-")]
                ]

frame_layout1 = [   [sg.Text('x-axis'), sg.InputText(key = "-Current_position_x-" ,size=(10, 1))],
                    [sg.Text('y-axis'), sg.InputText(key = "-Current_position_y-" ,size=(10, 1))],
                    [sg.Text('z-axis'), sg.InputText(key = "-Current_position_z-" ,size=(10, 1))]
                ]

frame_layout2 = [   [sg.Text('Current x velocity'), sg.InputText(key = "-Current_x_end_velocity-" ,size=(10, 1)), 
                     sg.Text('New x velocity'), sg.InputText(key = "-New_x_end_velocity-" ,size=(10, 1)), sg.Button('Update x Velocity')],
                    [sg.Text('Current y velocity'), sg.InputText(key = "-Current_y_end_velocity-" ,size=(10, 1)), 
                     sg.Text('New y velocity'), sg.InputText(key = "-New_y_end_velocity-" ,size=(10, 1)), sg.Button('Update y Velocity')],
                    [sg.Text('Current z velocity'), sg.InputText(key = "-Current_z_end_velocity-" ,size=(10, 1)), 
                     sg.Text('New z velocity'), sg.InputText(key = "-New_z_end_velocity-" ,size=(10, 1)), sg.Button('Update z Velocity')]
                ]


# Create the layout for the GUI
layout = [  [sg.Text('Mapper GUI')],
            [sg.Frame('Move axis', frame_layout0)], 
            [sg.Frame('Current position', frame_layout1)],
            [sg.Frame('Axis velocity', frame_layout2)],
            [sg.Button('Initialize'), sg.Button('Shutdown')]]

# Create the window
window = sg.Window('Mapper GUI', layout)


# Function to update the current position
def update_position():
    # Display the current position
    window['-Current_position_x-'].update(carrier.get_position(float(0)))
    window['-Current_position_y-'].update(carrier.get_position(float(1)))
    window['-Current_position_z-'].update(carrier.get_position(float(2)))


# Function to get all axis end velocity
def update_axis_end_velocity():
    # Display the current velocity
    window['-Current_x_end_velocity-'].update(carrier.get_end_velocity(0))
    window['-Current_y_end_velocity-'].update(carrier.get_end_velocity(1))
    window['-Current_z_end_velocity-'].update(carrier.get_end_velocity(2))

while True:
    event, values = window.read(timeout=0)
    
    update_position()
    update_axis_end_velocity()    
    
    move_x = values["-Move_X-"]
    move_y = values["-Move_Y-"]
    move_z = values["-Move_Z-"]
    non_safe_mode = values["-Non_safe_mode-"]

    if event == sg.WIN_CLOSED or event == 'Shutdown': # if user closes window or clicks shutdown
        # shutdown the carrier
        carrier.shutdown()
        window.close()
      
    # Move the x-axis
    if event == 'Move-x' and non_safe_mode == True:
        # call the move_to function from linact.py and read the input from the GUI
        carrier._move(float(move_x), 0)
    # Move the x-axis without checking the limit
    elif event == 'Move-x':
        # call the _move function from linact.py and read the input from the GUI
        carrier.move_to(float(move_x), 0)

    # Move the y-axis
    if event == 'Move-y' and non_safe_mode == True:
        # call the move_to function from linact.py and read the input from the GUI
        carrier._move(float(move_y), 1)
    # Move the y-axis without checking the limit
    elif event == 'Move-y':
        # call the _move function from linact.py and read the input from the GUI
        carrier.move_to(float(move_y), 1)

    # Move the z-axis
    if event == 'Move-z' and non_safe_mode == True:
        # call the move_to function from linact.py and read the input from the GUI
        carrier._move(float(move_z), 2)
    # Move the z-axis without checking the limit
    elif event == 'Move-z':
        # call the _move function from linact.py and read the input from the GUI
        carrier.move_to(float(move_z), 2)
    
    if event == 'Initialize':
        # initialize the carrier
        carrier.initialize()

    # Below is the code that update the end velocity
    carrier._set_end_velocity(0, values["-New_x_end_velocity-"])
    carrier._set_end_velocity(1, values["-New_y_end_velocity-"])
    carrier._set_end_velocity(2, values["-New_z_end_velocity-"])
    
window.close()