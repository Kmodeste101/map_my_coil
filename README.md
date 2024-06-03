Step Motor control
==================

For controlling a step motor with command line, you can use linact.py or using MapperGUI.py for a graphical interface.

Pre-requisites for MapperGUI.py
-------------------------------
inact.py and install PySimpleGUI (https://pysimplegui.readthedocs.io/en/latest/)

This GUI allows you to control a step motor in three axes (X, Y and Z) and adjust its speed and position.

* To move the step motor, use the “Move” button. You can select the axis and direction of the movement. The program will check the range limit before performing the movement, unless you check the “Non safe mode” box.

* To set the speed of the step motor, use the “Update Velocity” button. You can enter the speed in steps per second in the text field.

* To initialize the step motor at its current position, use the “Initialize” button. The step motor is initialized at position 0 when the program is launched.

* To exit the program and return the step motor to its initial position, use the “Shutdown” button.

Pre-requisites for linact.py
----------------------------
periphery.py

Before user can control the step motor, the user must initialize the stepper at its current position.

PDF Manual
----------
Simple Step Product Manual-2.pdf
