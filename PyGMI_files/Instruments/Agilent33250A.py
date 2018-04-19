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
        # self.io.write("OUTP:LOAD MAX")
        self.io.write("OUTP:LOAD 50")
        self.io.write("APPL:SIN 0.0, 0.0")
        
        """REM set function generator output to 6V p-p, attenuator to first estimate"""
        self.io.write("APPL:SIN 1.0E+3, 6.0")
        self.io.write("OUTP ON")
        
    def turn_off(self):
        logging.info("Ensure function generator provides zero output")
        self.io.write("APPL:SIN 0.0, 0.0")
        self.io.write("OUTP OFF")

    def set_frequency(self, freq, volt=0.0):
        logging.info("Set Agilent 33250A Frequency: %g", freq)
        self.io.write("APPL:SIN %g, %g" % (freq, volt))
        
    def start_burst(self, burst_count):
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
        TODO
        """
        logging.info("Generate a burst")
        # BURS:MODE TRIGGERED
        self.io.write("BURS:NCYC %d" % burst_count)
        burst_period = 1    # range from 1μs to 500s
        self.io.write("BURS:INT:PER %d" % burst_period) # TODO must be fixed to 0.25ms
        self.io.write("BURS:PHAS %d" % 0) # ALWAYS 0
        self.io.write("BURS:STAT ON")
        
    def stop_burst(self):
        self.io.write("BURS:STAT OFF")