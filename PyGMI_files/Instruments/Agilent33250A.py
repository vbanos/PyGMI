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
        # self.io.write("OUTP:LOAD MAX")
        self.io.write("OUTP:LOAD 50")
        #self.io.write("APPL:SIN 0, 0, 0") THIS CREATES AN ERROR
        
        """REM set function generator output to 6V p-p, attenuator to first estimate"""
        # commented out because it breaks SLM tone burst measurement 2018-05-14
        # self.io.write("APPL:SIN 1.0E+3, 6.0")
        self.io.write("OUTP 1")
        
    def turn_off(self):
        self.io.write("OUTP 0")

    def set_frequency(self, freq, volt=0.0):
        logging.info("Set Agilent 33250A Frequency: %g", freq)
        self.io.write("APPL:SIN %g, %g" % (freq, volt))
        
    def start_burst(self, freq, volt, delay, count):
        """Ref: Agilent 33250A manual
        Chapter 4 Remote Interface Reference, Burst Mode Commands, Page 187.
        
        Configure Burst waveform
        Use the APPLy command or the equivalent FUNC, FREQ, VOLT, and
        VOLT:OFFS commands to select the function, frequency, amplitude,
        and offset of the waveform. You can select a sine, square, ramp, pulse,
        or arbitrary waveform (noise is allowed only in the gated burst mode
        and dc is not allowed). For internally-triggered bursts, the minimum
        frequency is 2 mHz. For sine and square waveforms, frequencies above
        25 MHz are allowed only with an “infinite” burst count.
        
        ref: http://rfmw.em.keysight.com/spdhelpfiles/33500/webhelp/US/Content/__I_SCPI/BURSt_Subsystem.htm
        """
        logging.info("Generate a burst with %d cycles and %g delay" % (count, delay))
        self.io.write("OUTP 0")
        self.io.write("APPL:SIN %d,%g VPP, 0 V" % (freq, volt))
        self.io.write("BURS:MODE TRIG")
        self.io.write("TRIG:SOUR EXT")
        self.io.write("BURS:NCYC %d" % count)  # number of cycles from excel
        # Useful only for INTERNAL TRIGGER, WE USE EXTERNAL 
        #self.io.write("BURS:INT:PER %g" % period) # unit is seconds! 200ms, 2ms, 0.25ms
        self.io.write("TRIG:DEL %g" % delay)
        self.io.write("BURS:STAT ON")
        self.io.write("OUTP 1")
        logging.info("burst started")
        
    def stop_burst(self):
        time.sleep(2)
        self.io.write("BURS:STAT OFF")
        
    def positive_half_cycle(self, freq, volt):
        """Used Agilent Waveform editor to create POSRECT 8Khz, 0.1V and send it
        to the Agilent 33250A generator. If not available, you must send it again.
        file: Half_rectify.csv
        """
        self.io.write("FUNC:USER POSRECT")
        self.io.write("FREQ %d" % freq)
        self.io.write("VOLT %g" % volt)
        self.io.write("APPLY:USER %d, %g" % (freq, volt))
        self.io.write("OUTP 1")
        
    def negative_half_cycle(self, freq, volt):
        """Half_rectify_negative_vbanos.wvf.
        """
        self.io.write("FUNC:USER NEGRECT")
        self.io.write("FREQ %d" % freq)
        self.io.write("VOLT %g" % volt)
        self.io.write("APPLY:USER %d, %g" % (freq, volt))
        self.io.write("OUTP 1")
        