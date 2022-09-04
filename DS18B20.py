

#Address should be the full address of the device as it appears in the
#devices directory in the format '28-00000c801c26'
#
#The reading is two lines long in the format:
#  Line 0: 'b1 01 4b 46 7f ff 0f 10 8d : crc=8d YES'
#  Line 1: 'b1 01 4b 46 7f ff 0f 10 8d t=27062'

class DS18B20:
    def __init__(self, addr, TempInC = True):
        self._addr = addr
        self._FileLocation = '/sys/bus/w1/devices/'+self._addr+'/w1_slave'
        self.TempInC = TempInC  #True for C, false for F
        #self.retryNumber = 10  #TODO: Do I want this here?
    
    @property
    def Temperature(self):
        try:
            f = open(self._FileLocation, "r")
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            #No sensor at address
            #print("No sensor at address ", self._addr)
            return -500
        
        if (lines[0].strip()[-3:]) == 'YES':
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                #CRC ok, temp found
                temp_string = lines[1][equals_pos+2:]
                #print(temp_string)
                if self.TempInC:
                    return (float(temp_string) / 1000.0)
                else:
                    return (float(temp_string) / 1000.0)*(9.0 / 5.0) + 32.0
            else:
                #CRC ok, but no temp found in output file
                return -502
        else:
            #CRC error in reading
            return -501
        
def main():
    #28-00000c801c26
    int_sensor = DS18B20("28-00000c801c26", True)
    print(int_sensor.Temperature)
    int_sensor.TempInC = False
    print(int_sensor.Temperature)
        
if __name__=="__main__":
    main()