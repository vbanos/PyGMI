import logging 
import math
import numpy
import pprint
import threading
import time
from Tkinter import *
import tkMessageBox
import winsound
import yaml


class Standard61672(object):
    def frequency_weighting_tolerance_limits_61672(self, frequency_weighting, nominal_frequency, ref_spl, measured_spl,
                                                   windshiled_correction, case_correction):
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
           16000.0: {"A": -6.6, "C": -8.5, "Z": 0.0},
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
           16000.0: {1: {"min":-17.0, "max": 3.5}, 2: {"min": -1000.0, "max": 6.0}},
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
        
class Standard60651(object):
    def frequency_weighting_tolerance_limits_61672(self, frequency_weighting, nominal_frequency, ref_spl, measured_spl,
                                                   windshiled_correction, case_correction):
        # TODO different tables than 60672
        pass


class SlmData(object):
    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root)
        self.frame.pack()
        
        self.reference_SPL = DoubleVar()
        Label(self.frame, text="Reference SPL:").grid(row=0)        
        Entry(self.frame, textvariable=self.reference_SPL).grid(row=0, column=1)

        self.frequency_weighting = DoubleVar()
        Label(self.frame, text="Frequency Weighting:").grid(row=1)
        Entry(self.frame, textvariable=self.frequency_weighting).grid(row=1, column=1)
        
        self.linearity_range = DoubleVar()
        Label(self.frame, text="Linearity Range:").grid(row=2)
        Entry(self.frame, textvariable=self.linearity_range).grid(row=2, column=1)
        
        self.PIR_upper_limit = DoubleVar()
        Label(self.frame, text="PIR upper limit:").grid(row=3)
        Entry(self.frame, textvariable=self.PIR_upper_limit).grid(row=3, column=1)
        
        self.pulse_range = DoubleVar()
        Label(self.frame, text="Pulse Range:").grid(row=4)
        Entry(self.frame, textvariable=self.pulse_range).grid(row=4, column=1)
        
        self.min_slm_indication = DoubleVar()
        Label(self.frame, text="Min slm indication:").grid(row=5)
        Entry(self.frame, textvariable=self.min_slm_indication).grid(row=5, column=1)
        
        Label(self.frame, text="Level Ranges").grid(row=6, column=0)
        Label(self.frame, text="Upper").grid(row=6, column=1)
        Label(self.frame, text="Lower").grid(row=6, column=2)
                
        self.ref_upper_level_range = DoubleVar()
        self.ref_lower_level_range = DoubleVar()
        Label(self.frame, text="REF").grid(row=7)
        Entry(self.frame, textvariable=self.ref_upper_level_range).grid(row=7, column=1)
        Entry(self.frame, textvariable=self.ref_lower_level_range).grid(row=7, column=2)
        
        self.ref_level_ranges_upper = [DoubleVar() for _ in range(9)]
        self.ref_level_ranges_lower = [DoubleVar() for _ in range(9)]
        
        row = 8
        for i in range(len(self.ref_level_ranges_upper)):
            row += i
            Label(self.frame, text="").grid(row=row)
            Entry(self.frame, textvariable=self.ref_level_ranges_upper[i]).grid(row=row, column=1)
            Entry(self.frame, textvariable=self.ref_level_ranges_lower[i]).grid(row=row, column=2)
             
        row += 1
        Label(self.frame, text="Frequency").grid(row=row)
        Label(self.frame, text="Case Correction").grid(row=row, column=1)
        Label(self.frame, text="Windshield Correction").grid(row=row, column=2)
        
        row += 1
        labels = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 12500, 16000]
        self.case_corrections = [DoubleVar() for _ in range(11)]
        self.windshield_corrections = [DoubleVar() for _ in range(11)]
        for i in range(len(labels)):
            row += i
            Label(self.frame, text="%g Hz" % labels[i]).grid(row=row)
            Entry(self.frame, textvariable=self.case_corrections[i]).grid(row=row, column=1)
            Entry(self.frame, textvariable=self.windshield_corrections[i]).grid(row=row, column=2)

        b = Button(self.root,text='OK',command=self.get_selection)
        b.pack(side='bottom')

    def get_selection(self):
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()

    def waitForInput(self):
        self.root.mainloop()


class selectMethods(object):
    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root)
        self.frame.pack()
        
        self.frequency_weighting = IntVar()
        l = Checkbutton(self.root, text="Frequency Weighting", variable=self.frequency_weighting)
        l.pack()
        self.linearity = IntVar()
        l = Checkbutton(self.root, text="Linearity", variable=self.linearity)
        l.pack()
        self.time_weighting = IntVar()
        l = Checkbutton(self.root, text="Time Weighting", variable=self.time_weighting)
        l.pack()
        self.rms_accuracy = IntVar()
        l = Checkbutton(self.root, text="RMS Accuracy", variable=self.rms_accuracy)
        l.pack()
        self.peak_response = IntVar()
        l = Checkbutton(self.root, text="Peak Response", variable=self.peak_response)
        l.pack()
        self.time_averaging = IntVar()
        l = Checkbutton(self.root, text="Time Averaging", variable=self.time_averaging)
        l.pack()
        self.pulse_range = IntVar()
        l = Checkbutton(self.root, text="Pulse Range SEL and Overload", variable=self.pulse_range)
        l.pack()
        b = Button(self.root,text='OK',command=self.get_selection)
        b.pack(side='bottom')

    def waitForInput(self):
        self.root.mainloop()
        
    def get_selection(self):
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

    def gettext(self):
        self.string = self.e.get()
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()

    def getString(self):
        return self.string

    def waitForInput(self):
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
    # The following tables are optionally updated by the UI (tkinter forms).
    case_correction = {  31.5: 0.0,
                         63.0: 0.0,
                        125.0: 0.0,
                        250.0: 0.0,
                        500.0: 0.0,
                       1000.0: 0.0,
                       2000.0: 0.0,
                       4000.0: 0.0,
                       8000.0: 0.0,
                      12500.0: 0.0,
                      16000.0: 0.0}
    
    windshield_correction = {  31.5: 0.0,
                               63.0: 0.0,
                              125.0: 0.0,
                              250.0: 0.0,
                              500.0: 0.0,
                             1000.0: 0.0,
                             2000.0: 0.0,
                             4000.0: 0.0,
                             8000.0: 0.0,
                            12500.0: 0.0,
                            16000.0: 0.0}
            
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
               
        logging.info("init all instruments")
        measurement_options = SlmData()
        measurement_options.waitForInput()
        
        print("REF SPL", measurement_options.reference_SPL.get())
        
        
        self.std61672 = Standard61672()
        sys.exit(0)
        
        self.keithley2001 = m.instr_1   # GBIP0::16
        self.agilent3350A = m.instr_2   # GBIP0::20
        self.el100 = m.instr_3          # GBIP0::3
        
        
        
        
        
        # TODO make form to input SLM data
        #    Reference SPL    REF    
        #    Linearity Range
        #    PIR upper limit
        #    Pulse range
        #    min slm indicator
        #    Level ranges: upper - lower (2 values for each)
        #     e.g.    120 50
        #             130 60
        #             110 40
        #             100 30
        #              90 20
        #              80 10
        #             One of these is REF, we put this first
        self.slm_rev_value = 94.0
        
        standard = getText("Which standard do you use? 60651 or 61672-3?")
        
        if standard == "60651":
            self.run_60651()        
        elif standard == "61672-3":
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
                
        if options.frequency_weighting.get() == 1:
            self.frequency_weightings()
        if options.linearity.get() == 1:
            self.linearity()
        if options.time_weighting.get() == 1:
            self.time_weighting()
        if options.rms_accuracy.get() == 1:
            self.RMS_accuracy_and_overload()
        if options.peak_response.get() == 1:
            self.peak_response()
        if options.time_averaging.get() == 1:
            self.time_averaging()
        if options.pulse_range.get() == 1:
            self.pulse_range_SEL_and_overload()      
        
    def frequency_weightings(self):
        """TODO must do this 3 times for A, C and linear results       
        
        TODO initial el100 value 94 is not fixed. It is calculated by SLM manual values.
        max linearity range (e.g. 140) - 45 (fixed by standard 61672)
        
        we run the frequency weighting 3 times
        first time, we set SLM config to A weighting
        second time we set C weighting
        third time we set Z weighting.
        We do NOT change anything in our code/process, only SLM device settings change.
        # TODO popup, "Set SLM to A weighting and press any key when ready"
        # TODO popup              C weighting
        # TODO popup              Z weighting
        """
        self.el100_ref_value = getText("What is the attenuator value when SLM value is %g?" % self.slm_ref_value)
        
        self.el100.set("30.83")
        frequencies = [1000.0, 2000.0, 4000.0, 8000.0, 16000.0, 31.5, 63.0, 125.0, 250.0, 500.0]
        for weighting in ["A", "C", "Z"]:
            wait("Please set your Sound Level Meter to %s weighting and press any key to continue." % weighting)
            results = []
            for freq in frequencies:
                self.agilent3350A.set_frequency(freq, vol=4.0)
                slm_reading = float(getText("SLM reading (dB)?").strip())
                case_correction = self.case_correction[freq]
                windshield_correction = self.windshield_correction[freq]
                overall_response = slm_reading + case_correction + windshield_correction
                slm_class = self.std61672.frequency_weighting_tolerance_limits(
                    weighting, freq, 95.0, slm_reading, windshield_correction, case_correction)    
                
                row = [freq, slm_reading, windshield_correction, case_correction,
                       overall_response, slm_class]
                results.append(row)
        
            print("Frequency Weighting %s Results" % weighting)
            print("Frequency    Attn    Slm reading    Windshield corr    Case corr    Overall response    Class")
            print("   (Hz)      (dB)       (dB)            (dB)              (dB)            (dB)")
            for row in results:
                print("%.1f      %.2f        %.2f          %.2f              %.2f            %.2f            %d" % (
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6]))        
    
    def linearity(self):
        """TODO SET SPL and LEQ settings, run 2 times.
        """
        
        nominal_spls = [32.0, 33.0, 34.0, 35.0, 36.0, 39.0, 44.0, 49.0, 54.0, 59.0,
                        64.0, 69.0, 74.0, 79.0, 84.0, 89.0, 94.0, 99.0, 104.0, 109.0,
                        114.0, 119.0, 124.0, 126.0, 127.0, 128.0, 129.0, 130.0]
        attn_setting = [99.69, 98.67, 97.66, 96.63, 95.62, 92.59, 87.56, 82.54, 77.53, 72.52,
                        67.53, 62.53, 57.53, 52.53, 47.54, 42.53, 37.54, 32.54, 27.54, 22.54,
                        17.55, 12.55, 7.56, 5.56, 4.56, 3.56, 2.56, 1.56]
        
        results = []
        for i in range(len(nominal_spls)):
            self.el100.set(str(attn_setting[i]))
            noninal_spl = nominal_spls[i]
            diff_re_refspl = self.el100_ref_value - attn_setting[i]
            nom_diff = nominal_spl - self.el100_ref_value
            dvm_rdg = 0.0   # TODO keithley read channel
            
            
            # paragraph 5.5.5 of iso
            # if abs() > 1.4 it is class 2
            # else class 1
        
            slm_class = self._decide_class()   # TODO
            row = [nominal_spl, attn_setting[i], diff_re_refspl, nom_diff, dvm_rdg, slm_class]
            results.append(row)
        
        print("Linearity Test (SPL setting)    Ref range, A-weighting") # TODO other as well
        print("Nominal SPL    Attn Setting    Diff re RefSpl    Nom Diff    Dvm Rdg    Class")
        print("    (dB)            (dB)            (dB)            (dB)        (mV)")
        for row in results:
            print("    %.1f        %.2f        %.2f        %.2f    %.2f    %d" % (
                row[0], row[1], row[2], row[3], row[4], row[5]))
    
    def time_weighting(self):
        # TODO
        pass
    
    def RMS_accuracy_and_overload(self):
        # TODO ??
        # Attenuator adjusted to an SLM Reading of 123 dB for the continuous signal
        # Attenuator reading = 9.06 dB
        # SLM reading = 123.28 dB
        # Nominal reading = 123 dB
        
        # TODO signal increased until SLM overload ??
        # SLM Reading = 125.74 dB
        # Signal reduced by 1 dB    SLM Reading = 124.74 dB
        # Signal reduced by 3 dB    SLM Reading = 121.74 dB
        #     Nominal SLM Reading = 121.74 dB
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
    
    def pulse_range_SEL_and_overload(self):
        # TODO
        # 40 cycle bursts applied. Slm set to SEL and reset.
        # SLM reading = 70.05, 70.05, 70.05 dB
        
        
        pass
    
    def _decide_class(self):
        # TODO
        return 1
        