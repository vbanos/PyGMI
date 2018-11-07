import logging 
import threading
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilename
import yaml

from ..eim.tkutils import selectMethods616723, selectMethods60651
from PyGMI_files.eim.measurements60651 import (TimeWeighting60651, Linearity60651,
    FrequencyWeighting60651, PeakResponse60651, TimeAveraging60651, RmsAccuracyAndOverload60651,
    PulseRangeSoundExposureLevelAndOverload60651)
from PyGMI_files.eim.measurements616723 import (OverloadIndicationMeasurement616723,
    FrequencyTimeWeighting616723, ToneburstResponse616723, PeakCSoundLevel616723,
    AcousticTest616723, SelfGeneratedNoiseTest616723)


######create a separate thread to run the measurements without freezing the front panel######
class Script(threading.Thread):
                
    def __init__(self, mainapp, frontpanel, data_queue, stop_flag,
                 GPIB_bus_lock, **kwargs):
        threading.Thread.__init__(self,**kwargs)
        self.mainapp=mainapp
        self.frontpanel=frontpanel
        self.data_queue=data_queue
        self.stop_flag=stop_flag
        self.GPIB_bus_lock=GPIB_bus_lock
        
    def run(self):
        """General configuration is loaded from
        C:\acoustics-configuration\general.yaml 
        """
        #with open('C:/acoustics-configuration/slm-general.yaml', 'r') as stream:
        #    self.GENERAL_CONF = yaml.load(stream)     
        #    assert self.GENERAL_CONF.get('ITERATIONS')
        #    assert self.GENERAL_CONF.get('WAIT_BEFORE_SPL_MEASUREMENT')      
        # a shortcut to the main app, especially the instruments
        m = self.mainapp          
        
        logging.info("init all instruments")        
        self.keithley2001 = m.instr_1 # GBIP0::16
        self.wgenerator = m.instr_2   # GBIP0::20 Agilent GBIP::10 Keysight
        self.el100 = m.instr_3        # GBIP0::3
                                                
        logging.info("Load conf from yaml file")
        root = Tk()
        calibration_conf = askopenfilename(parent=root)
        with open(calibration_conf, 'r') as stream:
            self.conf = yaml.load(stream)
                                        
        if self.conf.get("standard") == "60651":
            self.run_60651()        
        elif self.conf.get("standard") == "61672-3":
            self.run_61672_3()
        else:
            logging.error("No valid standard selected")
            sys.exit(0)
    
    def run_60651(self):
        """Old standard - also known as BS7580
        """
        # TODO add conf variable PIR_INDICATOR_RANGE: 125
        
        options = selectMethods60651()
        options.waitForInput()
        
        if options.acoustic_test.get():
            self.acoustic_test()
        if options.self_generated_noise_test.get():
            self.self_generated_noise_test()
        if options.frequency_weighting.get():
            # TODO question: 60651 results have a PASS/FAIL column.
            # This is the only difference between 60651 and 61672-3.
            fw = FrequencyWeighting60651(self.conf, self.el100, self.wgenerator,
                                        self.keithley2001)
            fw()
        if options.linearity.get():            
            li = Linearity60651(self.conf, self.el100, self.wgenerator,
                                self.keithley2001)
            li()
        if options.time_weighting.get():
            tw = TimeWeighting60651(self.conf, self.el100, self.wgenerator,
                                    self.keithley2001)
            tw()            
        if options.rms_accuracy_and_overload.get():
            rms = RmsAccuracyAndOverload60651(self.conf, self.el100,
                                              self.wgenerator, self.keithley2001)
            rms()
        if options.peak_response.get():
            pr = PeakResponse60651(self.conf, self.el100, self.wgenerator,
                                   self.keithley2001)
            pr()      
        if options.time_averaging.get():
            ta = TimeAveraging60651(self.conf, self.el100, self.wgenerator,
                                    self.keithley2001)
            ta()
        if options.pulse_range_sound_exposure_level_and_overload.get():
            pu = PulseRangeSoundExposureLevelAndOverload60651(self.conf,
                self.el100, self.wgenerator, self.keithley2001)
            pu()            
            
        print("END OF MEASUREMENTS")
        sys.exit(0)
    
    def run_61672_3(self):
        """New standard
        """
        options = selectMethods616723()
        options.waitForInput()
        if options.acoustic_test.get():
            # NOTE that its the same method as ISO std 60651.
            ac = AcousticTest616723(self.conf, self.el100, self.wgenerator,
                                    self.keithley2001)
            ac()
        if options.self_generated_noise_test.get():
            # NOTE that its the same method as ISO std 60651.
            se = SelfGeneratedNoiseTest616723(self.conf, self.el100, self.wgenerator,
                                              self.keithley2001)
            se()   
                         
        if options.frequency_weighting.get():
            # NOTE that its the same method as ISO std 60651.
            fw = FrequencyWeighting60651(self.conf, self.el100, self.wgenerator,
                                         self.keithley2001)
            fw()
        if options.linearity.get():
            # NOTE that its the same method as ISO std 60651.
            li = Linearity60651(self.conf, self.el100, self.wgenerator,
                                self.keithley2001)
            li()
        if options.freq_time_weighting.get():
            ft = FrequencyTimeWeighting616723(self.conf, self.el100, self.wgenerator,
                                              self.keithley2001)
            ft()
        if options.overload_indication.get():
            ov = OverloadIndicationMeasurement616723(self.conf, self.el100, self.wgenerator,
                                                     self.keithley2001)
            ov()
        if options.peak_C_sound_level.get():
            pe = PeakCSoundLevel616723(self.conf, self.el100, self.wgenerator,
                                       self.keithley2001)
            pe()
        if options.toneburst_response.get():
            to = ToneburstResponse616723(self.conf, self.el100, self.wgenerator,
                                         self.keithley2001)
            to()
        print("END OF MEASUREMENTS")
        sys.exit(0)