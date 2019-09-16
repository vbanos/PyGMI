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
        
    # Reference Table 5.16, chapter 5-15. Racal operators manual
    # NOTE that A channel X10 attenuator is turned on/off randomly when
    # turning on/off the measured instrument.
    CONFIG = ["AAC",
              "AAD",
              "AFE",
              "AHI",
              "APS",
              "SLA0.0"
              "SRS8",
              "AAU"]
        
    def read(self):
        """Return float
        SRS8 = 5 digits accuracy
        FA = Frequency A
        """
        for cmd in self.CONFIG:
            self.io.write(cmd)
        result = self.io.ask("")
        return float(result.replace("FA+", ""))
    
    def read_only(self):
        """Return float
        SRS6 = 3 digits accuracy
        FA = Frequency A
        """
        result = self.io.ask("")
        return float(result.replace("FA+", ""))
    
    def read_list(self, times=1, delay=0.0):
        for cmd in self.CONFIG:
            self.io.write(cmd)
        results = []
        for _ in range(times):
            results.append(self.read_only())
            time.sleep(delay)
            print("Read Racal")
        return results
    
    def read_average(self, times=1, delay=0.0):
        """Read N times with a delay interval. Return mean value.
        """
        results = self.read_list(times, delay)
        print(results)
        return round(float(sum(results) / len(results)), 3)