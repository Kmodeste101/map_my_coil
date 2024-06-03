import logging
from typing import Dict
"""
Version: 1.0.0
@author: Michael Beck
@date: Feb  5, 2020
University of Winnipeg
"""

"""
An abstract class for periphery classes to inherit from.

:param parameters: Name-Value pairs of the periphery in a dictionary
:param constants: Name-Value pairs of not to be changed parameters in a dict.
:raises OutOfLimitException: when a parameter is set out of bounds 
"""


class PeripheryException(Exception):
    pass


class OutOfLimitException(PeripheryException):
    """Exception raised when setting parameters out of bounds"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Periphery:
    def __init__(self, name: str, parameters: Dict, constants=None):
        self.parameters = parameters
        self.constants = constants
        self.logger = logging.getLogger('MainLogger.'+name)
        self.logger.info('Initializing')

    def initialize(self):
        """Set the periphery to a starting state, e.g. going to home"""
        pass

    def shutdown(self):
        """Shut down the periphery"""
        self.logger.info('Shutting down')
        pass

    def set_par(self, parameter: str, value) -> bool:
        """Set a parameter. Return false, if that parameter does not exist"""
        if parameter in self.parameters.keys():
            self.parameters[parameter] = value
            return True
        else:
            self.logger.warning(
                    "{0} parameter does not exist".format(parameter))
            return False

    def get_par(self, *args):
        """Return value of parameter(s) or dict of all parameters"""
        # Return dictionary of ALL parameters
        if len(args) == 0:
            return self.parameters
        # Return parameter itself
        if len(args) == 1:
            return self.parameters[args[0]]
        # Return list of parameters
        else:
            return [self.parameters[p] for p in args]

    def get_const(self):
        return self.constants
