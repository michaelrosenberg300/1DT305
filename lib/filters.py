class DigitalFilters:
#
# Base class for digital filters. Only limited functionality implemented.
#
    def __init__(self, M, x0):
        self.M = M                          # Odd number, length of filter
        self.x0 = x0                        # Initial value of filter states

        self.FilterStates = [x0]*M          # Create the initial filter states
        self.y = x0                         # The current output from filter

class MovingAverage(DigitalFilters):
#
# This class provides an efficient implementation of a moving average filter
#
    def Update(self, x):
        xOld = self.FilterStates.pop()       # Get and remove the oldest x-value from the list
        self.FilterStates.insert(0, x)       # Add the new x-value first in the list

        self.y = self.y + (x - xOld)/self.M
        return self.y
