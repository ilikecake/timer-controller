
import time
import board
from digitalio import DigitalInOut, Direction
from PCAL9554 import PCAL9554
import busio
import adafruit_sht4x
from DS18B20 import DS18B20

#Capabiltiy bits
# 0: temperature
# 1: Humidiity
# 3: Digital Input

#TempUnits:
#   0: F
#   1: C

class sensor:
    def __init__(self, bus, sensor_type, sensor_address, capability, TempUnits):
        self._bus = bus
        self._sensor_type = sensor_type
        self._sensor_address = sensor_address
        self._capability = capability
        self._TempUnits = TempUnits
        if (self._sensor_type == "SHT40"):
            self._dev = adafruit_sht4x.SHT4x(self._bus)
            self._dev.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
        elif (self._sensor_type == "DS18B20"):
            if(self._TempUnits == 1):
                self._dev = DS18B20(self._sensor_address, True)
            else:
                self._dev = DS18B20(self._sensor_address, False)
    
    @property
    def temperature(self) -> float:
        if ( (self._capability & (1<<0)) == 0x01):
            if (self._sensor_type == "SHT40"):
                #print("reading from SHT40")
                if (self._TempUnits == 1):
                    return self._dev.temperature
                else:
                    return self._dev.temperature*(9.0 / 5.0) + 32.0
            if (self._sensor_type == "DS18B20"):
                return self._dev.Temperature
            print("sensor not handled")
        else:
            print("Sensor not temperature capable")
            
    @property
    def humidity(self) -> float:
        if ( (self._capability & (1<<1)) == (1<<1)):
            if (self._sensor_type == "SHT40"):
                print("reading from SHT40")
                return self._dev.relative_humidity
            print("sensor not handled")
        else:
            print("Sensor not humidity capable")
        #functs:
        #    temperature
        #    humidiry
        #    digital_val
        #   Pressure
            

class sensor_hw:
    def __init__(self, i2c, TempInC = True):
        self._i2c = i2c
        self._IOExp = PCAL9554(self._i2c)
        #self._addr = addr
        #self._FileLocation = '/sys/bus/w1/devices/'+self._addr+'/w1_slave'
        self.TempInC = TempInC  #True for C, false for F
        #self.retryNumber = 10  #TODO: Do I want this here?
        
        #Define GPIO pins
        self._1wire_enable = DigitalInOut(board.D15)
        self._GPIO_Pins = [DigitalInOut(board.D21), DigitalInOut(board.D26), DigitalInOut(board.D19), DigitalInOut(board.D20)]
        self._TWI_PWR_enable = self._IOExp.get_pin(5)
        self._TWI_data_enable = self._IOExp.get_pin(7)
        self._TWI_PWR_flt = self._IOExp.get_pin(4)
        self._TWI_data_ready = self._IOExp.get_pin(6)
        self._DDR_Pins = [self._IOExp.get_pin(0), self._IOExp.get_pin(1), self._IOExp.get_pin(2), self._IOExp.get_pin(3)]
        
        #configure pins
        self._1wire_enable.direction = Direction.OUTPUT
        self._1wire_enable.value = True
        
        self._TWI_PWR_enable.direction = Direction.OUTPUT
        self._TWI_PWR_enable.value = False
        
        self._TWI_data_enable.direction = Direction.OUTPUT
        self._TWI_data_enable.value = False
        
        #GPIO Data Direction
        # DDR high = output
        for DDR in self._DDR_Pins:
            DDR.direction = Direction.OUTPUT
            #DDR.value = True
            
        #for GPIO_pin in self._GPIO_Pins:
        #    GPIO_pin.direction = Direction.OUTPUT
        #    GPIO_pin.value = False
        
        self.GPIO_Dir(1, Direction.OUTPUT)
        self.GPIO_Dir(2, Direction.OUTPUT)
        self.GPIO_Dir(3, Direction.OUTPUT)
        self.GPIO_Dir(4, Direction.OUTPUT)
        
        self.GPIO_SetVal(1, False)
        self.GPIO_SetVal(2, False)
        self.GPIO_SetVal(3, False)
        self.GPIO_SetVal(4, False)
        
    def Enable_1wire(self):
        self._1wire_enable.value = True
        
    def Disable_1wire(self):
        self._1wire_enable.value = False
        
    def Enable_TWI(self):
        self._TWI_PWR_enable.value = True
        #time.sleep(.1)
        self._TWI_data_enable.value = True
        
    def Disable_TWI(self):
        self._TWI_data_enable.value = False
        self._TWI_PWR_enable.value = False
    
    #DDR dir=true for output
    #TODO: use the Direction.INPUT/OUTPUT here?
    #dir_to_set should be Direction.OUTPUT/INPUT
    def GPIO_Dir(self, pin, dir_to_set):
        if (pin >= 1) and (pin <= 4):
            if (dir_to_set == Direction.OUTPUT):
                self._DDR_Pins[pin-1].value = True
                self._GPIO_Pins[pin-1].direction = dir_to_set
            else:
                self._DDR_Pins[pin-1].value = False
                self._GPIO_Pins[pin-1].direction = dir_to_set
        
    def GPIO_SetVal(self, pin, value_to_set):
        if (pin >= 1) and (pin <= 4):
            if (self._DDR_Pins[pin-1].value):   #TODO: This catches trying to set a GPIO setup as an input to an output value. Do I want to silently catch this?
                self._GPIO_Pins[pin-1].value = value_to_set
        
def main():
    i2c = busio.I2C(board.SCL, board.SDA)

    #IOExpander1 = PCAL9554(i2c)
    SensorArray = sensor_hw(i2c, False)
    SensorArray.Enable_1wire()
    SensorArray.Enable_TWI()
    
    sensorlist = []
    sensorlist.append(sensor(i2c, "SHT40", 0x44, 0x03, 0))
    sensorlist.append(sensor(None, "DS18B20", "28-00000c801c26", 0x01, 0))
    
    #sensor1 = sensor(i2c, "SHT40", 0x44, 0x03, 0)
    print(sensorlist[0].temperature)
    print(sensorlist[0].humidity)
    
    #sensor2 = sensor(None, "DS18B20", "28-00000c801c26", 0x01, 0)
    print(sensorlist[1].temperature)
    print(sensorlist[1].humidity)
    #sht = adafruit_sht4x.SHT4x(i2c)
    #print("Found SHT4x with serial number", hex(sht.serial_number))

    #sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
    # Can also set the mode to enable heater
    # sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
    #print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])

    while True:
        #temperature, relative_humidity = sht.measurements
        #print("Temperature: %0.1f C" % temperature)
        #print("Humidity: %0.1f %%" % relative_humidity)
        print("")
        time.sleep(5)
    
    
        #print("disable")
        #SensorArray.Disable_1wire()
        #SensorArray.Disable_TWI()
        #SensorArray.GPIO_SetVal(1, False)
        #i2c_pwr.value = False
        #time.sleep(5)   #sec?
        #print("enable")
        #SensorArray.Enable_1wire()
        #SensorArray.Enable_TWI()
        #SensorArray.GPIO_SetVal(1, True)
        #i2c_pwr.value = True
        #time.sleep(5)   #sec?
        
if __name__=="__main__":
    main()