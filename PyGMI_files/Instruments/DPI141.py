# -*- coding: utf-8 -*-
import logging
import sys
import time
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Connect_Instrument():
    
    def __init__(self, VISA_address="GPIB0::2"):
        self.io = visa.instrument(VISA_address)
         
    def initialize(self):
        """commands executed when the instrument is initialized.
        """
        logging.info("initialise - configure instrument DPI141")
    
    def read(self):
        return float(self.io.read())
    
    def read_average(self, times=1, delay=0.0):
        """Read N times with a delay interval. Return mean value.
        """
        results = []
        for _ in range(times):
            results.append(self.read())
            time.sleep(delay)
        return float(sum(results) / len(results))