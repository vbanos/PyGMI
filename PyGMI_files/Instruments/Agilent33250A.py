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
        logging.info("Init Agilent 33250A %s", self.io.ask("*IDN?"))
        
    def initialize(self):
        """commands executed when the instrument is initialized"""
        self.io.write("*CLS")
        logging.info("CLS* => Clear all registers and logs")       
    
    def turn_on(self):
        """Frequency 1000, Amplitude 0, volt offset 0
        Volts unit is VPP (Volt Peak to Peak)
        """
        logging.info("Ensure function generator provides zero output")
        self.io.write("APPL:SIN 1.0E+3, 0.0")
        
        """REM set function generator output to 6V p-p, attenuator to first estimate"""
        # devicefreq = 1000 TODO ASKS YIANNIS ??
        self.io.write("APPL:SIN 1.0E+3, 6.0")