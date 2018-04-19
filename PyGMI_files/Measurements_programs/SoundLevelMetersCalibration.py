import logging 
import math
import numpy
import pprint
import threading
import time
from Tkinter import *
import ttk
from tkFileDialog import askopenfilename
import tkMessageBox
import winsound
import yaml


class Standard61672(object):
    def frequency_weighting_tolerance_limits(self, frequency_weighting,
                                             nominal_frequency, ref_spl,
                                             measured_spl, windshiled_correction,
                                             case_correction):
        """ISO61672-1 IEC:2002, Table 2, Page 33.
        Frequency_weighting = 'A', 'C' or 'Z'
        NOTE that there is a standard uncertainty budget = 0.21
        The final result will be 1, 2 or 3 (fail)
        """
        table_freq_weightings = {
            1000.0: {"A": 0.0, "C": 0.0, "Z": 0.0},
            2000.0: {"A": 1.2, "C": -0.2, "Z": 0.0},
            4000.0: {"A": 1.0, "C": -0.8, "Z": 0.0},
            8000.0: {"A": -1.1, "C": -3.0, "Z": 0.0},
           12500.0: {"A": -4.3, "C": -6.2, "Z": 0.0},
           16000.0: {"A": -6.6, "C": -8.5, "Z": 0.0},
              31.5: {"A": -39.4, "C": -3.0, "Z": 0.0},
              63.0: {"A": -26.2, "C": -0.8, "Z": 0.0},
             125.0: {"A": -16.1, "C": -0.2, "Z": 0.0},
             250.0: {"A": -8.6, "C": 0.0, "Z": 0.0},
             500.0: {"A": -3.2, "C": 0.0, "Z": 0.0}
        }
        tolerance_limits = {
            1000.0: {1: {"min":-1.1, "max": 1.1}, 2: {"min": -1.4, "max": 1.4}},
            2000.0: {1: {"min":-1.6, "max": 1.6}, 2: {"min": -2.6, "max": 2.6}},
            4000.0: {1: {"min":-1.6, "max": 1.6}, 2: {"min": -3.6, "max": 3.6}},
            8000.0: {1: {"min":-3.1, "max": 2.1}, 2: {"min": -5.6, "max": 5.6}},
           12500.0: {1: {"min":-6.0, "max": 3.0}, 2: {"min": -1000.0, "max": 6.0}},
           16000.0: {1: {"min":-17.0, "max": 3.5}, 2: {"min": -1000.0, "max": 6.0}},
              31.5: {1: {"min":-2.0, "max": 2.0}, 2: {"min": -3.5, "max": 3.5}},    
              63.0: {1: {"min":-1.5, "max": 1.5}, 2: {"min": -2.5, "max": 2.5}},
             125.0: {1: {"min":-1.5, "max": 1.5}, 2: {"min": -2.0, "max": 2.0}},
             250.0: {1: {"min":-1.4, "max": 1.4}, 2: {"min": -1.9, "max": 1.9}},
             500.0: {1: {"min":-1.4, "max": 1.4}, 2: {"min": -1.9, "max": 1.9}},
            }
        ref_spl += table_freq_weightings[nominal_frequency][frequency_weighting]
        dif = round(measured_spl - ref_spl, 2) + windshiled_correction + case_correction
        if(dif >= 0.0):
            dif += 0.21
        else:
            dif -= 0.21
        
        if tolerance_limits[nominal_frequency][1]["min"] <= dif <= tolerance_limits[nominal_frequency][1]["max"]:
            return 1
        elif tolerance_limits[nominal_frequency][2]["min"] <= dif <= tolerance_limits[nominal_frequency][2]["max"]:
            return 2
        else:
            return 3
        
    def linearity_tolerance_limits(self, deviation, uncertainty):
        """Use to define the class in Linearity measurement. Ref: ISO paragraph 5.5.5.
        Return 1, 2 or 3 (foul).
        """
        total = abs(deviation) + uncertainty
        if total <= 1.1:
            return 1
        elif total <= 1.4:
            return 2
        else:
            return 3
        
class Standard60651(object):
    def frequency_weighting_tolerance_limits(self, frequency_weighting,
                                             nominal_frequency, ref_spl,
                                             measured_spl, windshiled_correction,
                                             case_correction):
        # TODO different tables than 60672
        pass
    
# TODO accoustical signal Par. 11

class selectMethods(object):
    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root)
        self.frame.pack()
        
        # 61672-3 Electrical Tests Par. 12  
        self.frequency_weighting = IntVar()
        self.frequency_weighting_chk = ttk.Checkbutton(self.root, text="Frequency Weighting",
                                                       variable=self.frequency_weighting)
        self.frequency_weighting_chk.pack()
        
        # 61672-3 Electrical Tests Par. 14 & 15
        self.linearity = IntVar()
        self.linearity_chk = Checkbutton(self.root, text="Linearity", variable=self.linearity)
        self.linearity_chk.pack()
        
        # 61672-3 Electrical Tests Par. 13 TODO change name to Frequency and time weighting
        self.time_weighting = IntVar()
        self.time_weighting_chk = Checkbutton(self.root, text="Time Weighting", variable=self.time_weighting)
        self.time_weighting_chk.pack()
        
        # 61672-3 Electrical Tests Par. 18 TODO change name Overload indication    
        self.rms_accuracy = IntVar()
        self.rms_accuracy_chk = Checkbutton(self.root, text="RMS Accuracy", variable=self.rms_accuracy)
        self.rms_accuracy_chk.pack()
        
        # # 61672-3 Electrical Tests Par. 17 TODO change name Peak C sound level
        self.peak_response = IntVar()
        self.peak_response_chk = Checkbutton(self.root, text="Peak Response", variable=self.peak_response)
        self.peak_response_chk.pack()
        
        # 61672-3 Electrical Tests Par. 16 Tone burst response       
        
        
        """
        self.time_averaging = IntVar()
        self.time_averaging_chk = Checkbutton(self.root, text="Time Averaging", variable=self.time_averaging)
        self.time_averaging_chk.pack()
        
        self.pulse_range = IntVar()
        self.pulse_range_chk = Checkbutton(self.root, text="Pulse Range SEL and Overload", variable=self.pulse_range)
        self.pulse_range_chk.pack()
        """
        
        b = Button(self.root,text='OK',command=self.get_selection)
        b.pack(side='bottom')

    def waitForInput(self):
        self.root.mainloop()
        
    def get_selection(self):
        
        self.frequency_weighting_checked = 'selected' in self.frequency_weighting_chk.state()
        self.linearity_checked = 'selected' in self.linearity_chk.state()
        self.time_weighting_checked = 'selected' in self.time_averaging_chk.state()
        self.rms_accuracy_checked = 'selected' in self.rms_accuracy_chk.state()
        self.peak_response_checked = 'selected' in self.peak_response_chk.state()
        self.time_averaging_checked = 'selected' in self.time_averaging_chk.state()
        self.pulse_range_checked = 'selected' in self.pulse_range_chk.state()
        
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()

class takeInput(object):
    """Utility class to show popup and get user input string.
    """
    def __init__(self,requestMessage):
        self.root = Tk()
        self.string = ''
        self.frame = Frame(self.root)
        self.frame.pack()        
        self.acceptInput(requestMessage)

    def acceptInput(self,requestMessage):
        r = self.frame

        k = Label(r,text=requestMessage)
        k.pack(side='left')
        self.e = Entry(r,text='Name')
        self.e.pack(side='left')
        self.e.focus_set()
        b = Button(r,text='okay',command=self.gettext)
        b.pack(side='right')
        
    def gettext(self, *args, **kwargs):
        self.string = self.e.get()
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()

    def getString(self):
        return self.string

    def waitForInput(self):
        self.root.bind('<Return>', self.gettext)
        self.root.mainloop()

def getText(requestMessage):
    msgBox = takeInput(requestMessage)
    #loop until the user makes a decision and the window is destroyed
    msgBox.waitForInput()
    msg = msgBox.getString().strip()
    return msg

def wait(msg):
    """Wait until any key is pressed.
    """
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    Tk().wm_withdraw() #to hide the main window
    tkMessageBox.showinfo("Calibration",msg)

######create a separate thread to run the measurements without freezing the front panel######
class Script(threading.Thread):
                
    def __init__(self,mainapp,frontpanel,data_queue,stop_flag,GPIB_bus_lock,**kwargs):
        #nothing to modify here
        threading.Thread.__init__(self,**kwargs)
        self.mainapp=mainapp
        self.frontpanel=frontpanel
        self.data_queue=data_queue
        self.stop_flag=stop_flag
        self.GPIB_bus_lock=GPIB_bus_lock
        
    def run(self):
        """General configuration is loaded from C:\acoustics-configuration\general.yaml 
        """
        #with open('C:/acoustics-configuration/slm-general.yaml', 'r') as stream:
        #    self.GENERAL_CONF = yaml.load(stream)     
        #    #assert self.GENERAL_CONF.get('ITERATIONS')
        #    #assert self.GENERAL_CONF.get('WAIT_BEFORE_SPL_MEASUREMENT')      

        m=self.mainapp              #a shortcut to the main app, especially the instruments
        f=self.frontpanel           #a shortcut to frontpanel values
        reserved_bus_access=self.GPIB_bus_lock     #a lock that reserves the access to the GPIB bus
               
        logging.info("Load conf from yaml file")
        root = Tk()
        calibration_conf = askopenfilename(parent=root)
        with open(calibration_conf, 'r') as stream:
            self.conf = yaml.load(stream)
        
        self.std61672 = Standard61672()
        
        logging.info("init all instruments")        
        self.keithley2001 = m.instr_1   # GBIP0::16
        self.agilent3350A = m.instr_2   # GBIP0::20
        self.el100 = m.instr_3          # GBIP0::3
                
        if self.conf.get("standard") == "60651":
            self.run_60651()        
        elif self.conf.get("standard") == "61672-3":
            self.run_61672_3()
        else:
            logging.error("No valid standard selected")
            sys.exit(0)
    
    def run_60651(self):
        """Old standard
        """
        # TODO
        pass
    
    def run_61672_3(self):
        """New standard
        """
        options = selectMethods()
        options.waitForInput()      
                        
        if options.frequency_weighting_checked:
            self.frequency_weightings()
        if options.linearity_checked:
            self.linearity()
        if options.time_weighting_checked:
            self.time_weighting()
        if options.rms_accuracy_checked:
            self.RMS_accuracy_and_overload()
        if options.peak_response_checked:
            self.peak_response()
        if options.time_averaging_checked:
            self.time_averaging()
        if options.pulse_range_checked:
            self.pulse_range_SEL_and_overload()      
        print("END OF MEASUREMENTS")
        sys.exit(0)
        
        
    def frequency_weightings(self):
        """TODO initial el100 value 94 is not fixed. It is calculated by SLM manual values.
        Max linearity range (e.g. 140) - 45 (fixed by standard 61672)
        
        We run the frequency weighting 3 times (A, C, Z).
        We do NOT change anything in our code/process, only SLM device settings change.
        reference SPL comes from the manufacturer.
        """
        linear_operating_range = self.conf.get("linear_operating_range")
        self.agilent3350A.set_frequency(1000.0, volt=0.5)
        
        spl_aim = linear_operating_range.get("max") - 45
        
        self.el100_ref_value = float(getText(
            "What is the attenuator value when SLM value is %g?" % spl_aim))
        
        frequencies = self.conf.get('frequencies')
        case_corrections = self.conf.get('case_corrections')
        windshield_corrections = self.conf.get('windshield_corrections')
        level_ranges = self.conf.get('level_ranges')
        upper_ref_level_range = level_ranges[0][0]
        lower_ref_level_range = level_ranges[0][1]
        for weighting in ["A", "C", "Z"]:
            wait("Please set your Sound Level Meter REF level range (%g, %g) and %s weighting and press any key to continue." % (
                upper_ref_level_range, lower_ref_level_range, weighting))
            results = []
            for freq in frequencies:
                self.agilent3350A.set_frequency(freq, volt=4.0)
                slm_reading = float(getText("Frequency = %g. What is the SLM reading (dB)?" % freq))    
                overall_response = slm_reading + case_corrections[freq] + windshield_corrections[freq]
                slm_class = self.std61672.frequency_weighting_tolerance_limits(
                    weighting, freq, 95.0, slm_reading, windshield_corrections[freq], case_corrections[freq])    
                
                row = [freq, self.el100_ref_value, slm_reading, windshield_corrections[freq], case_corrections[freq],
                       overall_response, slm_class]
                results.append(row)
        
            print("Frequency Weighting %s Results" % weighting)
            print("Frequency    Attn    Slm reading    Windshield corr    Case corr    Overall response    Class")
            print("   (Hz)      (dB)       (dB)            (dB)              (dB)            (dB)")
            for row in results:
                print("%.1f      %.2f        %.2f          %.2f              %.2f            %.2f            %d" % (
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6]))        
    
    def linearity(self):
        """TODO the problem is that we need to set an ACPP value to get attenuator ~ 50+-10.
        If we get initial attenuator value very low or high, there will a problem with other measurements.
                                
        2. tune attenuator until SPL = 99 (94 + 5) ... 
                
        uncertainty is fixed 0.2     
        
        COLUMNS
        Nominal SPL (dB)    Attn Setting (dB)    Diff ref  RefSPL    Nom Diff    Deviation    Uncertainty (dB) Class
        """
        linear_operating_range = self.conf.get('linear_operating_range')
        linear_operating_range_lower = linear_operating_range.get('min')
        ref_point_linearity_check = 94 # FIXED value
        linear_operating_range_upper = linear_operating_range.get('max')      
        
        range_upper = range(ref_point_linearity_check, int(linear_operating_range_upper) - 4, 5) + \
                        range(int(linear_operating_range_upper) -4, int(linear_operating_range_upper) + 1)
        
        range_lower = range(ref_point_linearity_check, int(linear_operating_range_lower) + 5, -5) + \
                        range(int(linear_operating_range_lower) + 5, int(linear_operating_range_lower) - 1)
        
        logging.info("ranges")
        logging.info(range_lower)
        logging.info(range_upper)

        wait("Please configure SLM to A weighting at reference level range [%g, %g]." % (
             linear_operating_range_lower,linear_operating_range_upper))
        
        self.agilent3350A.set_frequency(self.conf.get('generator_frequency'),
                                        volt=self.conf.get('generator_voltage'))  # ACPP (peak to peak). TODO what is the correct volt value??
        
        # TODO save keithley value after we set agilent frequency for ALL linearity measurements       
        ref_attenuation = float(getText("What is the attenuator value when SLM reads %g (dB)?" % ref_point_linearity_check))        
        
        results = []
        for slm in range_upper:
            atten = float(getText("What is the attenuator value when SLM reads %g (dB)?" % slm))
            # SKIP line when atten = 0 (cannot reach the SLM value)
            if atten == 0.0:
                continue
            dif_ref_refspl = slm -  ref_point_linearity_check # TODO ???
            nom_dif = slm -  ref_point_linearity_check
            deviation = dif_ref_refspl - nom_dif
            voltage = self.keithley2001.query_voltage()
            uncertainty = 0.2
            linearity_class = self.std61672.linearity_tolerance_limits(deviation, uncertainty)
            results.append([atten, dif_ref_refspl, nom_dif, deviation, uncertainty, voltage, linearity_class])
            
        for slm in range_lower:
            atten = float(getText("What is the attenuator value when SLM reads %g (dB)?" % slm))
            # SKIP line when atten = 0 (cannot reach the SLM value)
            if atten == 0.0:
                continue
            dif_ref_refspl = slm -  ref_point_linearity_check # TODO ???
            nom_dif = slm -  ref_point_linearity_check
            deviation = dif_ref_refspl - nom_dif
            voltage = self.keithley2001.query_voltage()
            uncertainty = 0.2
            linearity_class = self.std61672.linearity_tolerance_limits(deviation, uncertainty)
            results.append([atten, dif_ref_refspl, nom_dif, deviation, uncertainty, voltage, linearity_class])
                       
        print("Linearity Test")
        print("Nominal SPL    Attn Setting    Diff re RefSpl    Nom Diff    Dvm Rdg    Voltage Class")
        print("    (dB)            (dB)            (dB)            (dB)       (dB)      (V)         ")
        for row in results:
            print("    %.1f        %.2f        %.2f        %.2f        %.2f    %.2f        %d" % (
                row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        
        """if level ranges has multiple values beyond REF, perform extra test.
        Document reference: New IEC Standards and Periodic Testing of Sound Level Meters.
        Section 6.9, standard 61672-3 clause 15.2 15.3 15.4
        Note that agilent is already set to 8000 Hz and volt TODO ACPP
        """
        self.agilent3350A.set_frequency(1000.0, volt=self.conf.get('generator_voltage'))
        level_ranges = self.conf.get('level_ranges')
        if len(level_ranges) > 1:
            ref_atten = None
            ref_slm = None
            results = []
            for lrange in level_ranges[1:]:
                wait("Please configure SLM to A weighting at reference level range [%g, %g]." % (lrange[0], lrange[1]))
                wait("Please set attenuator value to %f" % ref_attenuation)
                slm = float(getText("What is the SLM value?"))
                if not ref_slm:
                    ref_slm = slm                    
                deviation = ref_slm - slm
                uncertainty = 0.2
                linearity_class = self.std61672.linearity_tolerance_limits(deviation, uncertainty)
                results.append(["%.2f - %.2f" % (lrange[0], lrange[1]),
                                ref_slm,
                                slm,
                                deviation,
                                uncertainty,
                                linearity_class])
                    
            def _print_slm_range_results(results):
                print("SLM range setting    Expected value    SLM Reading value    Deviation    Uncertainty    Class")
                print("      (dB)                (dB)                (dB)            (dB)            (dB)        ")
                for row in results:
                    print("    %s        %.2f           %.2f            %.2f        %.2f          %d" % (
                        row[0], row[1], row[2], row[3], row[4], row[5]))
        
            _print_slm_range_results(results)
        
            """Document reference: New IEC Standards and Periodic Testing of Sound Level Meters.
            Section 6.9, standard 61672-3 clause 15.4
            """
            results = []
            self.agilent3350A.set_frequency(1000.0, volt=self.conf.get('generator_voltage'))
            ref_atten = float(getText("What is the attenuator value when SLM reads %g (dB) (upper limit - 5)?" % lrange[1] - 5))
            for lrange in level_ranges[1:]:
                wait("Please configure SLM to A weighting at reference level range [%g, %g]." % (lrange[0], lrange[1]))
                slm = float(getText("What is the SLM value?"))
                if not ref_slm:
                    ref_slm = slm                    
                deviation = ref_slm - slm
                uncertainty = 0.2
                linearity_class = self.std61672.linearity_tolerance_limits(deviation, uncertainty)
                results.append(["%.2f - %.2f" % (lrange[0], lrange[1]),
                                ref_slm,
                                slm,
                                deviation,
                                uncertainty,
                                linearity_class])
        
            _print_slm_range_results(results)
    
    def time_weighting(self):
        """Ref: row 131 of excel 2250Asteroskopeio
        """
        ref_point_linearity_check = 94 # FIXED value
        self.agilent3350A.set_frequency(1000.0, volt=2.0)
        ref_attenuation = float(getText("What is the attenuator value when SLM reads %g (dB)?" % ref_point_linearity_check))
        
        #level_ranges = self.conf.get('level_ranges')
        #upper_ref_level_range = level_ranges[0][0]
        #lower_ref_level_range = level_ranges[0][1]
        #results = []
        #ref_atten = None
        """
        
            wait("Please set your Sound Level Meter REF level range (%g, %g) and %s weighting and press any key to continue." % (
                upper_ref_level_range, lower_ref_level_range, weighting))
            
            atten = float(getText("What is the attenuator value when SLM reads %g (dB)?" % slm))
            if weighting == "A":
                ref_atten = atten

            uncertainty = 0.2
                
            results.append([weighting,])
        """
        # TODO attenuator value ???
        
        # FAST time weighting
        results = []
        for weighting in ["A", "C", "Z"]:
            slm = float(getText("Please set your SLM to %s weighting and write your SLM value." % weighting))
            deviation = ref_point_linearity_check - slm
            uncertainty = 0.2
            time_weighting_class = self.std61672.linearity_tolerance_limits(deviation, uncertainty)
            results.append([weighting,
                            ref_point_linearity_check,
                            slm,
                            deviation,
                            uncertainty,
                            time_weighting_class])
        
        print("Time weighting F    Expected Value    SLM reading value    Deviation    Uncertainty    Class")
        print("                         (dB)               (dB)              (dB)          (dB)")
        for row in results:
            print("%s        %.2f        %.2f        %.2f        %.2f        %d" % (row[0], row[1], row[2], row[3], row[4], row[5]))
        
        # SLOW time weighting
        for weighting in ["A", "C", "Z"]:
            slm = float(getText("Please set your SLM to %s weighting and write your SLM value." % weighting))
            deviation = ref_point_linearity_check - slm
            uncertainty = 0.2
            time_weighting_class = self.std61672.linearity_tolerance_limits(deviation, uncertainty)
            results.append([weighting,
                            ref_point_linearity_check,
                            slm,
                            deviation,
                            uncertainty,
                            time_weighting_class])
        print("Time weighting S    Expected Value    SLM reading value    Deviation    Uncertainty    Class")
        print("                         (dB)               (dB)              (dB)          (dB)")
        for row in results:
            print("%s        %.2f        %.2f        %.2f        %.2f        %d" % (row[0], row[1], row[2], row[3], row[4], row[5]))
        
    def RMS_accuracy_and_overload(self):
        """Attenuator adjusted to an SLM Reading of X dB for the continuous signal
        # X = ref upper range - 1
        
        # TODO level overload indication (positive half cycle)
        # program Agilent to make a custom positive waveform
        
        # TODO level overload indication (negative half cycle)
        # program Agilent to make a custom negative waveform.
        # excel line 359.
        
        # Attenuator reading = 9.06 dB
        # SLM reading = 123.28 dB
        # Nominal reading = 123 dB
        
        # TODO signal increased until SLM overload ??
        # SLM Reading = 125.74 dB
        # Signal reduced by 1 dB    SLM Reading = 124.74 dB
        # Signal reduced by 3 dB    SLM Reading = 121.74 dB
        #     Nominal SLM Reading = 121.74 dB
        # 
        # attenuator increase step = 0.5 dB WARNING when we find overload, we should
        # tune to the previous value
        # then use step = 0.1 dB until the first indication of overload.
        """
        level_ranges = self.conf.get('level_ranges')
        upper_ref_level_range = level_ranges[0][0]
        lower_ref_level_range = level_ranges[0][1]
        weighting = "A"
        wait("Please set your Sound Level Meter REF level range (%g, %g) and %s weighting and press any key to continue." % (
                upper_ref_level_range, lower_ref_level_range, weighting))
        atten = float(getText("What is the attenuator value when SLM reads %g (dB)?" % 123))    # TODO
        
        # intial 139 using agilent 4 kHz normal waveform # save the atten value
        
        # switch to positive half cycle
        # initial value SLM | atten | overload value SLM after tweaking atten | atten | diff SLM (dB) | uncertainty | class
        #   136                    141
        
        # negative half cycle
        # do the same as positive
        
        #while(True):
            # TODO reduce attenuator ? How much?
            # WRITE line atten value | SLM value
            # WriTE line atten value | SLM value
            # ... Overflow at SLM on value X. Step size?
        
        
        pass 
    
    def peak_response(self):
        #TODO
        pass
    
    def time_averaging(self):
        # TODO
        self.el100.set("31.8")
        # function generator set to burst, Slm to Leq and attenuator adjusted by -30dB
        self.el100.set("41.8")
        # function generator set to burst, Slm to Leq and attenuator adjusted by -40dB
        self.el100.set("76.25")
        # channel 1 reconnected and adjusted to read 90 dB
        # 40 cycle bursts applied, Slm set to Leq and reset
        # SLM reading after 10s = X   Y    Z 
        # Nominal Reading = X dB
        pass
    
    def tone_burst(self):
        # continuous setting = LAF
        # Fast setting = LAF MAX
        # Slow setting = LAS MAX
        # LA eq (equivalent)
        pass
    
    def pulse_range_SEL_and_overload(self):
        # TODO
        # 40 cycle bursts applied. Slm set to SEL and reset.
        # SLM reading = 70.05, 70.05, 70.05 dB
        
        pass
        