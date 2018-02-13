# -*- coding: utf-8 -*-
import logging
import sys
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Connect_Instrument():
    def __init__(self, VISA_address="GPIB0::03"):
        self.io = visa.instrument(VISA_address, term_chars = "\r\n")
        logging.info("Init instrument GDS EL100")      
        
    def initialize(self):
        """commands executed when the instrument is initialized"""
        pass
        
    def set(self, value_str):
        """Input value string is a float like: "12,34"
        Each number corresponds to a char (ref EL100 manual tables).
        We write these chars to the device configure it.
        """
        c1 = self._first_char(value_str[0])
        c2 = self._second_char(value_str[1])
        c3 = self._third_char(value_str[3])
        c4 = self._forth_char(value_str[4])
        res = c1 + c2 + c3 + c4
        self.io.write(res)    
        
    def _first_char(self, c):
        c = int(c)
        values = range(64, 74)
        return chr(values[c])
    
    def _second_char(self, c):
        c = int(c)
        values = range(80, 90)
        return chr(values[c])
    
    def _third_char(self, c):
        c = int(c)
        values = range(96, 106)
        return chr(values[c])
        
    def _forth_char(self, c):
        c = int(c)
        values = range(112, 122)
        return chr(values[c])