# -*- coding: utf-8 -*-
import logging
import sys
import time
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Connect_Instrument():
    
    def __init__(self, VISA_address="GPIB0::4"):
        self.io = visa.instrument(VISA_address)
        logging.info("Init instrument Krohn-Hite 6880A")
         
    def initialize(self):
        """commands executed when the instrument is initialized.
        REM setup bk2636 filter (device, 1%=ext filter off, 0%=HPF on, 0%=LPF on, 4%=no weighting)
        CALL BK2636.filt (bk2636%, 1%, 0%, 0%, 4%, t..00001%)
        REM setup bk2636 gain (device, 1%=Ref off, 1%=Preamp Input, i/p gain as above, 5%=0 dB o/p gain)
        CALL BK2636.gain (bk2636%, 1%, 1%,  gain%, 5%, t..00001%)
        REM setup bk2636 detector (device, 0%=linear scale, 8%=Fast, 0%=Normal o/p, 0%=Fast Pk Decay, 0%=5dB Pk rise)
        """
        logging.info("initialise - configure instrument Krohn-Hite 6880A")
    
    def read_value(self):
        return float(self.io.read())
    
    def read(self, times=1, delay=0.0):
        """Read N times with a delay interval. Return mean value.
        """
        #logging.info("Kron Hite read %d times with delay %g", times, delay)
        results = []
        for _ in range(times):
            results.append(self.read_value())
            time.sleep(delay)
        return results