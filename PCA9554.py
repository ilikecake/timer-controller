# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods

"""
`mcp23017`
====================================================

CircuitPython module for the MCP23017 I2C I/O extenders.

* Author(s): Tony DiCola
"""

#Base I/O expander class for PCA9554 compatible IO expanders
#
#Compatible Devices
#	-PCA9554
#	-PCA9554A
#	-PCAL9554
#	-Lots of others...
#



from micropython import const
from adafruit_mcp230xx.mcp230xx import MCP230XX
from adafruit_mcp230xx.digital_inout import DigitalInOut
#from mcp230xx import MCP230XX	#removed relative import, might need this again if this is a module??
#from digital_inout import DigitalInOut	#removed relative import, might need this again if this is a module??

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx.git"

_PCA9554_ADDRESS = const(0x27)		#TODO: this will probably change based on the device used. Not sure how to deal with this. Maybe remove the default and force the user to specify the address?

_PCA9554_INPUT = const(0x00)	#Input register
_PCA9554_OUTPUT = const(0x01)	#Output register
_PCA9554_IPOL = const(0x02)		#Polarity inversion register
_PCA9554_IODIR = const(0x03)	#Configuration (direction) register

class PCA9554(MCP230XX):
    """Supports MCP23017 instance on specified I2C bus and optionally
    at the specified I2C address.
    """

    def __init__(self, i2c, address=_PCA9554_ADDRESS, reset=True):
        super().__init__(i2c, address)
        if reset:
            # Reset to all inputs with no pull-ups and no inverted polarity.
            self.iodir = 0xFF		#Set all IOs to inputs
            self.ipol = 0x00		#Set polatiry inversion off for all pins

    @property
    def gpio(self):
        """The raw GPIO output register.  Each bit represents the
        output value of the associated pin (0 = low, 1 = high), assuming that
        pin has been configured as an output previously.
        """
        return self._read_u8(_PCA9554_INPUT)

    @gpio.setter
    def gpio(self, val):
        self._write_u8(_PCA9554_OUTPUT, val)

    @property
    def iodir(self):
        """The raw IODIR direction register.  Each bit represents
        direction of a pin, either 1 for an input or 0 for an output mode.
        """
        return self._read_u8(_PCA9554_IODIR)

    @iodir.setter
    def iodir(self, val):
        self._write_u8(_PCA9554_IODIR, val)

    def get_pin(self, pin):
        """Convenience function to create an instance of the DigitalInOut class
        pointing at the specified pin of this MCP23017 device.
        """
        if not 0 <= pin <= 7:
            raise ValueError("Pin number must be 0-7.")
        return DigitalInOut(pin, self)

    @property
    def ipol(self):
        """The raw IPOL output register.  Each bit represents the
        polarity value of the associated pin (0 = normal, 1 = inverted), assuming that
        pin has been configured as an input previously.
        """
        return self._read_u8(_PCA9554_IPOL)

    @ipol.setter
    def ipol(self, val):
        self._write_u8(_PCA9554_IPOL, val)