# -*- coding: utf-8 -*-
import logging
import sys
import time
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

#TODO channel option

#TODO filter (gia to AC mono)
# οταν μετράς σε χαμηλές συχνότητες να κόβει κάποιες πάνω από ένα όριο
# FILTER ON / OFF



class Connect_Instrument():
    """Potential values are: AC, DC.
    """
    instr_mode = 'AC'
    
    def __init__(self, VISA_address="GPIB0::16"):
        self.io = visa.instrument(VISA_address, term_chars = "\r\n")
        logging.info("Init instrument Racal-Dana")
        
    def initialize(self):
        """commands executed when the instrument is initialized"""
        pass
        
    def read(self):
        """Return float
        """
        self.io.write(".")
        self.io.write("FA")
        self.io.write("N")
        result = self.io.ask("")
        return float(result.replace("FA+", ""))
    
    def read_average(self, times=1, delay=0.0)
        """Read N times with a delay interval. Return mean value.
        """
        results = []
        for _ in range(times):
            results.append(self.read())
            time.sleep(delay)
        return float(sum(results) / len(results))