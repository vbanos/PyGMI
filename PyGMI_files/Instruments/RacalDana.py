# -*- coding: utf-8 -*-
import logging
import sys
import time
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


# WARNING Racal-Dana does not return anything if it does not get a signal.
# If you do self.io.ask("RUT") it will return a string.

class Connect_Instrument():
    """Potential values are: AC, DC.
    """   
    def __init__(self, VISA_address="GPIB0::14"):
        self.io = visa.instrument(VISA_address, term_chars = "\r\n")
        logging.info("Init instrument Racal-Dana")
        
    def initialize(self):
        """Commands executed when the instrument is initialized.
        """
        pass
        
    def read(self):
        """Return float
        SRS6 = 3 digits accuracy
        FA = Frequency A
        """
        self.io.write("SRS6; FA")
        result = self.io.ask("")
        return float(result.replace("FA+", ""))
    
    def read_list(self, times=1, delay=0.0):
        results = []
        for _ in range(times):
            results.append(self.read())
            time.sleep(delay)
            print("Read Racal")
        return results
    
    def read_average(self, times=1, delay=0.0):
        """Read N times with a delay interval. Return mean value.
        """
        results = self.read_list(times, delay)
        print(results)
        return round(float(sum(results) / len(results)), 3)