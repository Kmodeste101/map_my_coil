# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 20:56:24 2020

@author: Chen Yi, Michael Beck
University of Winnipeg
"""

from time import sleep
import serial
from serial.tools.list_ports import comports

from periphery import Periphery, OutOfLimitException


#   Constants
# Port prefixes
# Windows
# port_prefix = ''
# Linux
# port_prefix = '/dev/'
# conversion between motor steps and centimeters
# CM_PER_STEP = 0.0003125
# STEP_PER_CM = 3200
# limits of the gantry in centimeters
# X_MAX = 70.0
# X_MIN = -15.0
# Y_MAX = 45.0
# Y_MIN = -45.0
# Z_MAX = 60.0
# Z_MIN = -30.0
# Max-Velocities
# X_MAX_VEL = 6000
# Y_MAX_VEL = 6000
# Z_MAX_VEL = 6000
# Axes names
# AXES = ('X', 'Y', 'Z')
# AXES_B = (b'X', b'Y', b'Z')

# Main class
class Carrier(Periphery):

    def __init__(self, name: str = 'Linear Actuator', velocity: int = 6000):
        constants = {
            "Max_position": 80.0,
            "Min_position": 0.0,
            "Max_y_position": 30.0,
            "Min_y_position": -30.0,
            "Max_velocity": 10000,
            "Start_velocity": 100,
            "cm_per_step": 0.0003125,
            "steps_per_cm": 3200,
            "axis_bin_name": b'X', 
            "Max_Z_position": 80.0,
            "Min_Z_position": 0.0,
            'velocity': 6000
        }
        if 0 < velocity <= constants["Max_velocity"]:
            Periphery.__init__(self, name,
                               {"velocity": velocity}, constants)
            self.logger.debug("Linear actuator booting")

            self.serial_connection = self._connect()
            if self.serial_connection is None:
                self.logger.error("Linear actuator not connected")
        else:
            raise OutOfLimitException(
                {'velocity': velocity,
                 'Max_velocity': constants["Max_velocity"]},
                'Beyond max-velocity'
            )
    
    
    def _connect(self) -> serial.Serial:
        devices = comports()
        for device in devices:
            if device.pid == 21:
                port_name = device.device
                self.logger.info("Motion controller found at {0}".
                                 format(port_name))
                serial_connection = serial.Serial(port=port_name,
                                                  baudrate=115200)
                break
        else:
            # noinspection PyUnusedLocal
            serial_connection = None
            self.logger.info("No motion controller found")
            raise serial.SerialException("")
        return serial_connection

    # Initializes the stepper at its current position
    def initialize(self):
        """Open port and initialize starting position"""
        self.logger.info("Initializing...")
        if not self.serial_connection.is_open:
            self.serial_connection.open()

        self.logger.debug("Setting Power Mode")
        self._write(b'X0P3,128,17,0,Y0P3,128,17,0,Z0P3,128,17,0\r')
        self.logger.debug("Received: " + str(self._read()))

        self.logger.debug("Initialize origin at current position")
        self._write(b'X0N+0S,Y0N+0S,Z0N+0S\r')
        # Null (Zero/Home) Motor + Clockwise + Ignore the home sensor
        # and initialize the board at its current position
        self.logger.debug("Received: " + str(self._read()))

        self._set_velocities(self.parameters["velocity"],
                             self.parameters["velocity"],
                             self.parameters["velocity"],
                             self.constants["Start_velocity"],
                             self.constants["Start_velocity"],
                             self.constants["Start_velocity"])
        self.logger.debug("Set 1/8-step mode")
        self._write(b'X0H3,Y0H3,Z0H3\r')
        sleep(0.1)
        self.logger.debug("Received: " + str(self._read()))

    def shutdown(self):
        """Set to starting position, close port"""
        self.logger.info("Shutting down")
        # Clear buffer from potentially aborted previous commands
        self._read()
        # TODO: put starting position back to 0.0 once done in home office
        # shut down all the motors in different x, y, z
        self.move_to(0.0, 0)
        self.move_to(0.0, 1)
        self.move_to(0.0, 2)
        self.serial_connection.close()

    def move_to(self, new_position: float, axis: int) -> bool:
        """Moves robot to a given position. Checks software limits.
        Returns success"""

        # # Flip sign of movement
        # if axis == 0:
        #     new_position = -new_position

        # if axis == 1:
        #     new_position = -new_position

        # Check for coordinates being in-bound
        if not self._within_limit(new_position, axis):
            self.logger.warning("You are asking the gantry to go off limit!")
            self._print_range()
            return False

        # Calculate number of steps to take
        current_position = self.get_position(axis)
        x_steps = int((new_position - current_position) *
                      self.constants["steps_per_cm"])
        
        self.logger.debug(
            "Moving robot to coordinates: X={0}cm.".format(new_position)
        )
        if axis == 0:
            if x_steps >= 0:
                self._write(bytes('X0RNY-{0}\r'.format(x_steps), 'utf-8'))
            else:
                self._write(bytes('X0RNY+{0}\r'.format(-x_steps), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
            return True
        if axis == 1:
            if x_steps >= 0:
                self._write(bytes('Y0RNY-{0}\r'.format(x_steps), 'utf-8'))
            else:
                self._write(bytes('Y0RNY+{0}\r'.format(-x_steps), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
            return True

        if axis == 2:
            if x_steps >= 0:
                self._write(bytes('Z0RNY+{0}\r'.format(x_steps), 'utf-8'))
            else:
                self._write(bytes('Z0RNY-{0}\r'.format(-x_steps), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
            return True

    def _move(self, cm_to_move: float, axis: int):
        """Displace carrier by given amount. Does not check software limits"""
        # Limit switches and home switches are still triggered and will
        # result in a stop

        # Calculate number of steps to take from current position
        x_steps = int(cm_to_move * self.constants["steps_per_cm"])
        
        # Flip sign of movement
        # if axis == 0:
        #     cm_to_move = -cm_to_move

        # if axis == 1:
        #     cm_to_move = -cm_to_move
        print("Moving robot to coordinates: X={0}cm.".format(cm_to_move))
        if axis == 0:
            # Moving carrier
            if x_steps >= 0:
                self._write(bytes('X0RNY-{0}\r'.format(x_steps), 'utf-8'))
            else:
                self._write(bytes('X0RNY+{0}\r'.format(-x_steps), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
        if axis == 1:
            # Moving carrier
            if x_steps >= 0:
                self._write(bytes('Y0RNY-{0}\r'.format(x_steps), 'utf-8'))
            else:
                self._write(bytes('Y0RNY+{0}\r'.format(-x_steps), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
        if axis == 2:
            # Moving carrier
            if x_steps >= 0:
                self._write(bytes('Z0RNY+{0}\r'.format(x_steps), 'utf-8'))
            else:
                self._write(bytes('Z0RNY-{0}\r'.format(-x_steps), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))

    def get_position(self, axis: int) -> float:
        """Gets position from motor controller in cm"""
        if axis == 0:
            self._write(self.constants["axis_bin_name"] + b'0m\r')
            position = -self._to_cm(self._read())
            return position
        if axis == 1:
            self._write(b'Y' + b'0m\r')
            position = -self._to_cm(self._read())
            return position
        if axis == 2:
            self._write(b'Z' + b'0m\r')
            position = self._to_cm(self._read())
            return position

    def stop(self):
        self.logger.info("Stop signal received. Stopping the motors")
        self._write(b'X0*,Y0*,Z0*\r')
        self.logger.debug("Received:", self._read())

    def _read(self):
        sleep(0.1)
        received = b''
        while self.serial_connection.inWaiting() > 0:
            received += self.serial_connection.read(1)
        return received

    def _write(self, data):
        self.serial_connection.write(data)

    def _set_velocities(self, x_end, y_end, z_end, x_begin, y_begin, z_begin):
        # Set Start velocity (13,000 is fastest possible)
        self.logger.debug("Setting beginning velocity")
        self._write(bytes('X0B{0},Y0B{1},Z0B{2}\r'.format(x_begin,
                                                          y_begin,
                                                          z_begin),
                          'utf-8'))
        self.logger.debug("Received: " + str(self._read()))

        # Set End Velocity [Full Step: 1 (slowest) to 20,000 (fastest)]
        self.logger.debug("Setting end velocity")
        self._write(bytes('X0E{0},Y0E{1},Z0E{2}\r'.format(x_end, y_end, z_end),
                          'utf-8'))
        self.logger.debug("Received: " + str(self._read()))

    # handy functions
    def _to_cm(self, response) -> float:
        return float(response[3:-1].decode()) * self.constants["cm_per_step"]

    def _print_range(self):
        self.logger.info("The possible range of movement is:")
        self.logger.info(
            "{0} < X < {1} cm".format(self.constants["Min_position"],
                                      self.constants["Max_position"])
        )

    def _within_limit(self, position: float, axis: int) -> bool:
        if axis == 0:
            if position > self.constants["Max_position"] or \
                    position < self.constants["Min_position"]:
                return False
            else:
                return True
        if axis == 1:
            if position > self.constants["Max_y_position"] or \
                    position < self.constants["Min_y_position"]:
                return False
            else:
                return True
        
        if position > self.constants["Max_Z_position"] or \
                    position < self.constants["Min_Z_position"]:
                return False
        else:
            return True
    
    # Return current speed of the motor
    def get_velocity(self, axis: int):
        if axis == 0:
            self._write(b'X' + b'0v\r')
            speed = self._to_cm(self._read())
            return speed
        if axis == 1:
            self._write(b'Y' + b'0v\r')
            speed = self._read()
            return speed
        if axis == 2:
            self._write(b'Z' + b'0v\r')
            speed = self._to_cm(self._read()) 
            return speed * self.constants["steps_per_cm"]

    # Set begin velocity
    def _set_begin_velocity(self, axis: int, velocity: int):
        if axis == 0:
            self._write(bytes('X0B{0}\r'.format(velocity), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
        if axis == 1:
            self._write(bytes('Y0B{0}\r'.format(velocity), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
        if axis == 2:
            self._write(bytes('Z0B{0}\r'.format(velocity), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
    
    # Set end velocity
    def _set_end_velocity(self, axis: int, velocity: int):
        if axis == 0:
            self._write(bytes('X0E{0}\r'.format(velocity), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
        if axis == 1:
            self._write(bytes('Y0E{0}\r'.format(velocity), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
        if axis == 2:
            self._write(bytes('Z0E{0}\r'.format(velocity), 'utf-8'))
            self.logger.debug("Received: " + str(self._read()))
    
    # Get begin velocity
    def get_begin_velocity(self, axis: int):
        if axis == 0:
            self._write(b'X0b\r')
            # covert last 4 bytes to float
            speed = self._read()[3:-1]
            return speed
        if axis == 1:
            self._write(b'Y0b\r')
            speed = self._read()[3:-1]
            return speed
        if axis == 2:
            self._write(b'Z0b\r')
            speed = self._read()[3:-1]
            return speed
        
    # Get end velocity
    def get_end_velocity(self, axis: int):
        if axis == 0:
            self._write(b'X0e\r')
            # covert last 4 bytes to float
            speed = self._read()[3:-1]
            return speed
        if axis == 1:
            self._write(b'Y0e\r')
            speed = self._read()[3:-1]
            return speed
        if axis == 2:
            self._write(b'Z0e\r')
            speed = self._read()[3:-1]
            return speed

 