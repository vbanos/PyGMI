# -*- coding: utf-8 -*-
import logging
import sys
import time
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Connect_Instrument():
    """Potential values are: AC, DC.
    """
    def __init__(self, VISA_address="GPIB0::1"):
        self.io = visa.instrument(VISA_address)
        logging.info("Init Mensor 3340 %s", self.io.ask("*IDN?"))
        
    def initialize(self):
        """commands executed when the instrument is initialized"""
        pass       
            
    def read(self):
        return float(self.io.read().strip())