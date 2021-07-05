import machine
import filters
from micropython import const

# Useful "constants" to handle airflow
AIR_OUT = const(0)
AIR_IN = const(1)
UNKNOWN = const(2)

class Sensor:
#
# A general base class for all sensors. It only contains generic
# functionality like averageing of measurements and min/max values. Shall be
# used as a base class for each individual sensor.
#
    def __init__(self, M, T0, SensorName):

        # Initiate a moving average filter to get stable measurements
        self.T = 0
        self.T_avg = T0
        self.SensorName = SensorName

        self.MA = filters.MovingAverage(M, self.T_avg)

        # Initiate max and min values
        self.MaxT = -200
        self.MinT = 200

    def PerformMeasurement(self):

        # Update all metrics that are generic to a temperate gauge
        self.T_avg = self.MA.Update(self.T)
        self.MaxT = max(self.MaxT, self.T)
        self.MinT = min(self.MinT, self.T)

    def Get(self):
        # Return the latest measurement done
        return self.T

    def GetAverage(self):
        # Return the latest averaged measurement calculated
        return self.T_avg

    def GetMax(self):
        # Return the maximum measurement done
        return self.MaxT

    def GetMin(self):
        # Return the minimum measurement done
        return self.MinT

    def GetName(self):
        # Return the name of the sensor
        return self.SensorName


class AirFlowEstimator(Sensor):
#
# The class used to estimate the direction of the airflow
#
    def __init__(self, SensorName):

        self.State = UNKNOWN
        super().__init__(9, 0, SensorName)         # Create a filter of length 9

    def PerformMeasurement(self, T_delta):

        self.T = T_delta
        super().PerformMeasurement()

    def GetState(self):

        if abs(self.GetAverage()) > 2.0:     # If temperature difference is larger than 2 degrees...
            self.State = AIR_IN              # ... it is assumed that air is going in the "wrong" direction
        else:
            self.State = AIR_OUT

        return self.State


class MCP9700E(Sensor):
#
# A MCP9700E class that only contains things that are specific to the MCP9700E
# sensor like hot it is connected to the Pycom and how temperature is
# calculated from the measured voltage.
#
    def __init__(self, SensorName, pin):
        # Initiate the ADC input to be able to make measurements
        self.pin = pin

        self.adc = machine.ADC()
        self.apin = self.adc.channel(pin=self.pin)

        super().__init__(9, 0, SensorName)         # Create a filter of length 9

    def PerformMeasurement(self):
        #
        # From data sheets we get that the sensor is linear with sensitivity
        # 10mV/C and that for 0C the output is 500mV. This gives us
        #
        #   V_out = 10mv/C*T + 500mV which gives us the wanted temperature:
        #
        #   T = (V_out - 0.5)/0.01 (units in Volts and C)
        #

        V = self.apin.voltage()/1000    # Convert to V from mV
        self.T = (V-0.5)/0.01           # Convert to T from V

        super().PerformMeasurement()
