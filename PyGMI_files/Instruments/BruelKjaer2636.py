# -*- coding: utf-8 -*-
import logging
import sys
import visa

# set logging output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Connect_Instrument():
    
    def __init__(self, VISA_address="GPIB0::4"):
        self.io = visa.instrument(VISA_address)
        logging.info("Init instrument Bruel & Kjaer 2636")
         
    def initialize(self):
        """commands executed when the instrument is initialized.
        REM setup bk2636 filter (device, 1%=ext filter off, 0%=HPF on, 0%=LPF on, 4%=no weighting)
        CALL BK2636.filt (bk2636%, 1%, 0%, 0%, 4%, t..00001%)
        REM setup bk2636 gain (device, 1%=Ref off, 1%=Preamp Input, i/p gain as above, 5%=0 dB o/p gain)
        CALL BK2636.gain (bk2636%, 1%, 1%,  gain%, 5%, t..00001%)
        REM setup bk2636 detector (device, 0%=linear scale, 8%=Fast, 0%=Normal o/p, 0%=Fast Pk Decay, 0%=5dB Pk rise)
        
        gain is a parameter calculated by microphone sensitivity
        n%=Fmt(gain%,"%i<%s",igain$)
        IF micsensitivity#<-31.0# THEN
          gain%=gain%-1%
          IF micsensitivity#<-50.0# THEN
            gain%=gain%-2%
          ENDIF
        ENDIF
        
        NOTE: O3 = 20dB
              O4 = 10dB
              O5 = 0dB
        HELP: Manual page 56
        """
        logging.info("initialise - configure instrument")
        self.io.write("A1S1I4O4G0F8N0D0R0")
        logging.info("Ready!")