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
from PCA9554 import PCA9554	#removed relative import, might need this again if this is a module??
from digitalio import DigitalInOut	#Do i need this??
#import digitalio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx.git"

# Internal helpers to simplify setting and getting a bit inside an integer.
def _get_bit(val, bit):
    return val & (1 << bit) > 0


def _enable_bit(val, bit):
    return val | (1 << bit)


def _clear_bit(val, bit):
    return val & ~(1 << bit)

_PCAL9554_ADDRESS = const(0x27)		#TODO: this will probably change based on the device used. Not sure how to deal with this. Maybe remove the default and force the user to specify the address?

_PCAL9554_OUTPUT_DRIVE_1 = const(0x40)
_PCAL9554_OUTPUT_DRIVE_2 = const(0x41)
_PCAL9554_INPUT_LATCH = const(0x42)
_PCAL9554_PUPD_EN = const(0x43)
_PCAL9554_PUPD_SEL = const(0x44)
_PCAL9554_IRQ_MASK = const(0x45)
_PCAL9554_IRQ_STATUS = const(0x46)
_PCAL9554_OUTPUT_PORT_CONFIG = const(0x4F)

class PCAL9554(PCA9554):
    """Supports MCP23017 instance on specified I2C bus and optionally
    at the specified I2C address.
    """

    def __init__(self, i2c, address=_PCAL9554_ADDRESS, reset=True):
        super().__init__(i2c, address, reset)	#This initializes the PCA9554 compatible registers. Only do things here that are specific to the PCAL9554
        if reset:
            # Reset to all inputs with no pull-ups and no inverted polarity.
            self.iodir = 0xFF		#Set all IOs to inputs
            self.ipol = 0x00		#Set polatiry inversion off for all pins

    @property
    def pupd_en(self):
        """reads the pull up/down status
        """
        return self._read_u8(_PCAL9554_PUPD_EN)

    @pupd_en.setter
    def pupd_en(self, val):
        self._write_u8(_PCAL9554_PUPD_EN, val)
        
    @property
    def pupd_sel(self):
        """reads the pull up/down status
        """
        return self._read_u8(_PCAL9554_PUPD_SEL)

    @pupd_sel.setter
    def pupd_sel(self, val):
        self._write_u8(_PCAL9554_PUPD_SEL, val)
    
    #Enable interrupt on a pin. Interrupts are triggered by any state change of the pin.
    def set_int_pin(self, pin):
        self._write_u8(_PCAL9554_IRQ_MASK, _clear_bit(self._read_u8(_PCAL9554_IRQ_MASK), pin))
        self.gpio()     #Read from the input port register to clear interrupts
    
    #Disable interrupts on a pin.
    def clear_int_pin(self, pin):
        self._write_u8(_PCAL9554_IRQ_MASK, _set_bit(self._read_u8(_PCAL9554_IRQ_MASK), pin))
        self.gpio()     #Read from the input port register to clear interrupts. Not sure if I need this here...
    
    @property
    def get_int_status(self):
        return self._read_u8(_PCAL9554_IRQ_STATUS)
        