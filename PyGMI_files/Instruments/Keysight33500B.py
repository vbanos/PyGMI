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
    def __init__(self, VISA_address="GPIB0::10"):
        self.io = visa.instrument(VISA_address)
        logging.info("Init Keysight 33500B %s", self.io.ask("*IDN?"))
        
    def initialize(self):
        """commands executed when the instrument is initialised"""
        self.io.write("OUTP:LOAD 50")
        self.io.write("*CLS")
        logging.info("CLS* => Clear all registers and logs")       
    
    
    def turn_on(self):
        """Enable signal output.
        """
        self.io.write("OUTP 1")
        time.sleep(1)
        
    def turn_off(self):
        self.io.write("OUTP 0")
        time.sleep(1)

    def set_frequency(self, freq, volt=0.0, shape="SIN"):
        logging.info("Set Keysight 33500B Frequency: %g shape: %s", freq, shape)
        # self.io.write("FUNC:SHAP %s" % shape)
        self.io.write("APPL:%s %g, %g" % (shape, freq, volt))      
        
        # FUNCtion:SHAPe {SINusoid|SQUare|RAMP|USER} 
        
        # FUNCtion:SQUare:DCYCle {<percent>|MINimum|MAXimum} 
        
    def start_burst(self, freq, volt, delay, count, shape='SIN', period=None):
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
        
        Burst Documentation:
        http://rfmw.em.keysight.com/spdhelpfiles/33500/webhelp/US/Content/__I_SCPI/BURSt_Subsystem.htm
        """
        
        # NEW IMM burst
        if period:
            self.io.write("OUTP 0")
            # Breaks RmsAccuracyAndOverload measurement, this function should
            # have been already run earlier.
            # self.io.write("APPL:%s %d,%g VPP, 0 V" % (shape, freq, volt))
            self.io.write("BURS:MODE TRIG")
            self.io.write("BURS:NCYC %d" % count)
            self.io.write("BURS:INT:PER %g" % period)
            self.io.write("BURS:PHAS 0")
            self.io.write("TRIG:SOUR IMM")
            self.io.write("BURS:STAT ON")
            self.io.write("OUTP 1")
            return
        
        # TRIGGERED BURST
        # logging.info("Generate a burst with %d cycles and %g delay" % (count, delay))
        self.io.write("OUTP 0")
        self.io.write("APPL:%s %d,%g VPP, 0 V" % (shape, freq, volt))
        self.io.write("BURS:MODE TRIG")
        self.io.write("TRIG:SOUR EXT")
        self.io.write("BURS:NCYC %d" % count)  # number of cycles from excel
        # Useful only for INTERNAL TRIGGER, WE USE EXTERNAL 
        #self.io.write("BURS:INT:PER %g" % period) # unit is seconds! 200ms, 2ms, 0.25ms
        self.io.write("TRIG:DEL %g" % delay)
        self.io.write("OUTP 1")
        self.io.write("BURS:STAT ON")
        
    def stop_burst(self):
        time.sleep(2)
        self.io.write("BURS:STAT OFF")
        time.sleep(1)
        
    def positive_half_cycle(self, freq, volt, burst_count=None):
        """Used Agilent Waveform editor to create POSRECT 8Khz, 0.1V and send it
        to the Agilent 33250A generator. If not available, you must send it again.
        file: Half_rectify.csv
        """
        self.io.write("OUTP 0")           
        self.io.write('SOUR:FUNC:ARB "INT:\POSRECT.BARB"')
        sample_rate = freq * 1000
        self.io.write('SOUR:APPL:ARB %d, %d, 0' % (sample_rate, volt))
        if burst_count:
            self.io.write("BURS:MODE TRIG")
            self.io.write("TRIG:SOUR EXT")
            self.io.write("BURS:NCYC %d" % burst_count)  # number of cycles from excel
            self.io.write("TRIG:DEL 0")
            self.io.write("OUTP 1")
            self.io.write("BURS:STAT ON")
        else:
            self.io.write("OUTP 1")
        
    def negative_half_cycle(self, freq, volt, burst_count=None):
        """Half_rectify_negative_vbanos.wvf.
        
        SOUR:FUNC:ARB NEGRECT.BARB
        SOUR:FUNC:ARB INT:\MYARB.BARB
        -121 Invalid character in number
        
        SOUR:FUNC:ARB "INT:\MYARB.BARB"
        
        NO ERROR
        SOUR:FUNC:ARB "INT:\MYARB.BARB"
        SOUR:APPL:ARB 1000, 1, 0
        
        The previous POSRECT / NEGRECT do not work properly in Keysight 33500
        
        We must construct new functions.
        
        The sample rate must be 1000 so as to have freq = sample rate.
        
        http://rfmw.em.keysight.com/spdhelpfiles/33500/webhelp/US/Content/_Home_Page/Command_Quick_Reference.htm
        
        Keysight 33500 manual page 136
        The frequency at which points are read is the "sample rate," and the
        waveform frequency equals the sample rate divided by the number of points
        in the waveform. For example, suppose a waveform has 40 points and the
        sample rate is 10 MHz. The frequency would be (10 MHz)/40 = 250 kHz and
        its period would be 4 µs.
        
        We use 1000 points for POSRECT and REGRECT, the freq would be:
        freq = sample_rate / 1000 (points)
        
        """
        self.io.write("OUTP 0")
        self.io.write('SOUR:FUNC:ARB "INT:\NEGRECT.BARB"')
        sample_rate = freq * 1000
        self.io.write('SOUR:APPL:ARB %d, %d, 0' % (sample_rate, volt))
        
        if burst_count:
            self.io.write("BURS:MODE TRIG")
            self.io.write("TRIG:SOUR EXT")
            self.io.write("BURS:NCYC %d" % burst_count)  # number of cycles from excel
            self.io.write("TRIG:DEL 0")
            self.io.write("OUTP 1")
            self.io.write("BURS:STAT ON")
        else:
            self.io.write("OUTP 1")
        
    def get_frequency(self):
        self.io.write("FREQ?")
        return float(self.io.read().strip())
        
    def get_voltage(self):
        self.io.write("VOLT?")
        return float(self.io.read().strip())
        