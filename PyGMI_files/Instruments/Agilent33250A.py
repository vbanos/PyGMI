# -*- coding: utf-8 -*-
import logging
import sys
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Connect_Instrument():
    """Potential values are: AC, DC.
    """
    
    def __init__(self, VISA_address="GPIB0::20"):
        self.io = visa.instrument(VISA_address)
        logging.info("Init instrument %s", self.io.ask("*IDN?"))
        
    def initialize(self):
        """commands executed when the instrument is initialized"""
        self.io.write("*CLS")
        logging.info("CLS* => Clear all registers and logs")
        #self.set_measurement_mode("AC")

        