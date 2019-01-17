"""Measurement classes loaded by SoundLevelMetersCalibration.py
Methods for ISO 61672-3
"""
import logging
import time
from tkutils import wait, getText
from measurements60651 import BaseMeasurement


class OverloadIndicationMeasurement616723(BaseMeasurement):
    
    def __call__(self):
        """ISO61672-3 Paragraph 18
        least-sensitive level range with the sound level meter set to A-weighted time-average sound level.
        
        Attenuator adjusted to an SLM Reading of X dB for the continuous signal
        # target_db = ref upper range - 1
        # level overload indication (positive half cycle)
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
        self.reset_instruments()
        
        wtitle = "Overload Indication (61672-3 Electrical Tests Par.18)" 
        lrange = self.conf.get('least_sensitive_level_range')
        upper_range = lrange[0]
        lower_range = lrange[1]
        weighting = "A"
        wait("Please set your Sound Level Meter REF level range (%g, %g) and %s weighting and press any key to continue." % (
             upper_range, lower_range, weighting), title=wtitle)

        self.el100.set("20.00") # Must start with a high value and the decrease it
        slm_initial = upper_range - 1
        (target_volt, atten_positive) = self._tune_wgenerator(4000, slm_initial, wtitle)
                
        def _measure():    
            atten = atten_positive
            step = 0.5
            switch_step = True
            while(True):
                answer = getText("Do we have an overload in the Sound Level Meter? (y / n)").lower()
                if answer == "y":
                    if step == 0.5:
                        step = 0.1
                        logging.info("Switching to step 0.1")
                    elif step == 0.1:
                        # When we switch from 0.5 to 0.1, we go back 0.5. This happens only once.
                        if switch_step:
                            atten += 1.0
                            switch_step = False
                        
                        atten_overload = atten
                        slm_overload = float(getText("What is the current SLM value?"))
                        slm_diff = slm_overload - slm_initial
                        uncertainty = 0.2
                        myclass = 1 if -1.8 <= slm_diff <= 1.8 else 2
                        return (slm_initial, atten_positive, slm_overload,
                                atten_overload, slm_diff, uncertainty, myclass)
                else:                         
                    atten -= step
                self.el100.set("%05.2f" % atten)

        self.wgenerator.positive_half_cycle(freq=4000, volt=target_volt/2.0)
        all_results = []
        row = _measure()
        all_results.append(row)
        print("initial SLM | atten | overload SLM | atten | diff SLM | uncertainty | class")
        print("   %.2f     %.2f      %.2f      %.2f       %.2f       %.2f       %d" % (
              row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        self.wgenerator.turn_off()
        
        # TODO SET attenuator initial found value
        
        self.wgenerator.negative_half_cycle(freq=4000, volt=target_volt/2.0)
        row = _measure()
        all_results.append(row)
        self.wgenerator.turn_off()
        
        print("initial SLM | atten | overload SLM | atten | diff SLM | uncertainty | class")
        for row in all_results:
            print("   %.2f     %.2f      %.2f      %.2f       %.2f       %.2f     %d" % (
                  row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        self.reset_instruments()
    
        # BUG SLM in table 1 larger by result
        # INFO:root:SET EL100 VALUE 15.10
        # initial SLM | atten | overload SLM | atten | diff SLM | uncertainty | class
        # 99.00     18.30      96.70      16.00       -2.30       0.20     2
        # 99.00     18.30      96.60      16.10       -2.40       0.20     2


class FrequencyTimeWeighting616723(BaseMeasurement):
    def __call__(self):
        """ISO61672-3 Electrical Tests Par. 13
        Ref: row 131 of excel 2250Asteroskopeio
        """
        self.reset_instruments(el100=99.00)
        ref_point_linearity_check = 94 # FIXED value
        self.wgenerator.set_frequency(1000.0, volt=2.0)
        wait("Please configure the attenuator value so that SLM reads %g dB." % ref_point_linearity_check)
        ref_attenuation = self.el100.get()
                        
        # FAST time weighting
        results = []
        for weighting in ["A", "C", "Z"]:
            slm = float(getText("Please set your SLM to %sF weighting and write your SLM value." % weighting))
            deviation = ref_point_linearity_check - slm
            uncertainty = 0.2
            time_weighting_class = self.linearity_tolerance_limits(deviation, uncertainty)
            results.append([weighting,
                            ref_point_linearity_check,
                            slm,
                            deviation,
                            uncertainty,
                            time_weighting_class])
        
        print("Time weighting F    Expected Value    SLM reading value    Deviation    Uncertainty    Class")
        print("                         (dB)               (dB)              (dB)          (dB)")
        for row in results:
            print("%sF        %.2f        %.2f        %.2f        %.2f        %d" % (row[0], row[1], row[2], row[3], row[4], row[5]))
        
        
        results = []
        # SLOW time weighting
        for weighting in ["A", "C", "Z"]:
            slm = float(getText("Please set your SLM to %sS weighting and write your SLM value." % weighting))
            deviation = ref_point_linearity_check - slm
            uncertainty = 0.2
            time_weighting_class = self.linearity_tolerance_limits(deviation, uncertainty)
            results.append([weighting,
                            ref_point_linearity_check,
                            slm,
                            deviation,
                            uncertainty,
                            time_weighting_class])
        print("Time weighting S    Expected Value    SLM reading value    Deviation    Uncertainty    Class")
        print("                         (dB)               (dB)              (dB)          (dB)")
        for row in results:
            print("%sS        %.2f        %.2f        %.2f        %.2f        %d" % (row[0], row[1], row[2], row[3], row[4], row[5]))
        print("Attenuator value: %g" % ref_attenuation)
        self.reset_instruments()


class ToneburstResponse616723(BaseMeasurement):
    def __init__(self):
        """ISO61672-3 Electrical Tests Par. 16      
        Continuous setting = LAF
        Fast setting = LAF MAX
        Slow setting = LAS MAX
        LA eq (equivalent)
        """
        self.reset_instruments()
        wtitle = "Toneburst Response, ISO61672-3 Electrical Tests Par. 16"
        level_ranges = self.conf.get('level_ranges')
        upper_ref_level_range = level_ranges[0][0]
        lower_ref_level_range = level_ranges[0][1]
        weighting = "A"
        wait("Please set your Sound Level Meter REF level range (%g, %g) and %s weighting and press any key to continue." % (
             upper_ref_level_range, lower_ref_level_range, weighting), wtitle)
       
        slm_aim = upper_ref_level_range - 3.0
        
        (volt, atten) = self._tune_wgenerator(4000, slm_aim, wtitle)
    
        runs = [dict(setting="Fast (LAF MAX)",
                     opts=[dict(delay=0.2, cycles=800, offset=-1, min_tolerance=-0.8, max_tolerance=0.8),
                           dict(delay=0.002, cycles=8, offset=-18, min_tolerance=-1.8, max_tolerance=1.3),
                           dict(delay=0.00025, cycles=1, offset=-27, min_tolerance=-3.3, max_tolerance=1.3)]),
                dict(setting="Slow (LAF MAX)",
                     opts=[dict(delay=0.2, cycles=800, offset=-1, min_tolerance=-0.8, max_tolerance=0.8),
                           dict(delay=0.002, cycles=8, offset=-18, min_tolerance=-1.8, max_tolerance=1.3)]),
                dict(setting="LA eq (equivalent)",
                     opts=[dict(delay=0.2, cycles=800, offset=-1, min_tolerance=-0.8, max_tolerance=0.8),
                           dict(delay=0.002, cycles=8, offset=-18, min_tolerance=-1.8, max_tolerance=1.3),
                           dict(delay=0.00025, cycles=1, offset=-27, min_tolerance=-3.3, max_tolerance=1.3)])]
        
        for run in runs:
            results = []
            for opt in run['opts']:
                slm_results = []
                slm_expected = slm_aim + opt['offset']
                for _ in range(3):
                    wait("Please use SLM setting %s and reset instrument." % run['setting'])    
                    self.wgenerator.start_burst(freq=4000, volt=volt,
                                                  delay=opt['delay'], count=opt['cycles'])
                    self.wgenerator.stop_burst()
                    self.wgenerator.turn_off()
                    slm_reading = float(getText("Voltage = %g. What is the SLM reading (dB)?" % volt))  # TODO which var?
                    slm_results.append(slm_reading)
                slm_avg = sum(slm_results) / len(slm_results)
                slm_deviation = slm_avg - slm_expected
                uncertainty = 0.2
                if opt['min_tolerance'] <= slm_deviation <= opt['max_tolerance']:
                    myclass = 1
                else:
                    myclass = 2           
                result = [opt['delay'], opt['cycles'], opt['offset'], slm_expected,
                          slm_results[0], slm_results[1], slm_results[2], slm_avg,
                          slm_deviation, uncertainty, myclass]
                results.append(result)
            
            print(run['setting']) 
            print("Burst   Burst Cycles    LAFmax-LA   Expected    SLM    SLM    SLM   SLM   Deviation    Unc    Class")
            print("Delay                  (IEC 61672-1              m1     m2     m3   avg")   
            print("(ms)        (N)         Table 3)      (dB)      (dB)   (dB)   (dB)  (dB)   (dB)       (dB)")
            for r in results:
                print("%g       %g        %g        %g        %g    %g    %g    %g    %g        %g    %g" % (
                      r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))
        
        self.reset_instruments()
        

class PeakCSoundLevel616723(BaseMeasurement):
    def __call__(self): 
        """ISO61672-3 Paragraph 17
        Only for C-weighted sound level    NOTE C-weighting is Frequency Weighting option.
        Use least-sensitive sound range
        
        To set main variable = LCF in the SLM, do the following:
        measurement -> Edit display -> variable LAFMAX -> Edit field -> select from the list LAF
        -> Freq. Weighting button -> LCPeak or LCPeak max).  
        """
        self.reset_instruments()
        wtitle = "Peak C sound Level (61672-3 Electrical Tests Par.17)"
        lrange = self.conf.get('least_sensitive_level_range')
        upper_range = lrange[0]
        lower_range = lrange[1]
        weighting = "C"
        target_slm = upper_range - 8.0
        wait("Please set your Sound Level Meter to %s weighting, main variable LCF and the least sensitive level range (%g, %g)." % (
             weighting, upper_range, lower_range), title=wtitle)
        
        print("Peak C.    LCpeak-LC    Expected    SLM SLM  SLM    SLM    Deviation    Uncertainty    Class")
        print("Response                  (dB)       m1  m2   m3    avg       (dB)          (dB)") 
        
        def _measure_print(step, label, offset, target_volt):
            expected = target_slm + offset
            row = [label, offset,  expected]
            for _ in range(3):
                if step == 1:
                    self.wgenerator.start_burst(freq=8000, volt=target_volt,
                                                delay=0, count=1)
                elif step == 2:
                    self.wgenerator.positive_half_cycle(freq=500, volt=target_volt/2.0, # SOS
                                                        burst_count=1)
                elif step == 3:
                    self.wgenerator.negative_half_cycle(freq=500, volt=target_volt/2.0, # SOS
                                                        burst_count=1)
                self.wgenerator.stop_burst()
                self.wgenerator.turn_off()
                slm_val = float(getText("What is the SLM LCpeakMax value (dB)?"))                    
                row.append(slm_val)
                wait("Please reset your SLM.")
            slm_avg = (row[3] + row[4] + row[5]) / 3.0
            row.append(slm_avg)
            deviation = slm_avg - expected
            row.append(deviation)
            row.append(0.2) # uncertainty
            if step == 1:
                myclass = 1 if -1.4 < deviation < 1.4 else 2
            elif step == 2 or step == 3:
                myclass = 1 if -2.4 < deviation < 2.4 else 2
                    
            row.append(myclass)
            return row
        
        def _print_row(row):
            # TODO 2 decimal for SLM avg, deviation, uncertainty
            print("%s    %g    %g    %g    %g    %g    %g    %g    %g    %d" % (
                  row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                  row[8], row[9]))
        
        all_results = []
        # Steady 8Khz tuning
        (target_volt, target_atten) = self._tune_wgenerator(8000, target_slm, wtitle)
        print("Attenuator setting %g dB." % target_atten)
        
        # Steady 8Khz measurement
        self.wgenerator.set_frequency(freq=8000, volt=target_volt)
        slm_val = float(getText("What is the SLM LCF value (dB)?"))
        print("Steady 8Khz    %g    %g" % (target_slm, slm_val))
        self.wgenerator.turn_off()
        wait("Please reset your SLM.")
        
        # Burst with 1 cycle, 8Khz
        row = _measure_print(step=1, label="1 cycle 8Khz    ", offset=3.4,
                             target_volt=target_volt)       
        all_results.append(row)
        _print_row(row)
        
        # Steady 500Hz tuning
        (target_volt, target_atten) = self._tune_wgenerator(500, target_slm, wtitle)
        print("Attenuator setting %g dB." % target_atten)
        
        # Steady 500Hz measurement
        self.wgenerator.set_frequency(freq=500, volt=target_volt)
        slm_val = float(getText("What is the SLM LCF value (dB)?"))
        print("Steady 500Hz    %g    %g" % (target_slm, slm_val))
        self.wgenerator.turn_off()
        wait("Please reset your SLM.")
        
        # Positive half cycle 500Hz
        row = _measure_print(step=2, label="Positive half cycle", offset=2.4,
                             target_volt=target_volt)
        all_results.append(row)
        _print_row(row)
                
        # Negative half cycle 500Hz
        row = _measure_print(step=3, label="Negative half cycle", offset=2.4,
                             target_volt=target_volt)
        all_results.append(row)
        _print_row(row)
        self.reset_instruments()
        

class AcousticTest616723(BaseMeasurement):
    """ISO 61672-3 Par. 11, Page 19.
    
    11.1 Set SLM to C frequency weighting, if not available set A.
    
    """
    def __call__(self):
        """125 Hz, 1, 4, 8 Khz
        Excel line 24. TODO???
        """        
        wtitle = "Acoustic Test"
    
        calibrator_conf = self.conf.get('calibrator')
        # manufacturer: "B&K"
        # type: "4231"
        # serial_number: "2218152"
        # spl: 94.0     # from certificate
        # free_field_correction: -0.15        # from certificate
        # windscreen_correction: -0.2
        # pressure_correction: 0.0
        corrected_spl = calibrator_conf.get('spl') + \
                        calibrator_conf.get('free_field_correction') + \
                        calibrator_conf.get('windscreen_correction') + \
                        calibrator_conf.get('pressure_correction')
        
        lrange = self.conf.get('linear_operating_range')
        lrange_min = lrange.get("min")
        lrange_max = lrange.get("max")
        wait("Please connect customer SLM and EIM reference calibrator.", title=wtitle)
        wait("Please configure the SLM to use A weighting and range %g, %g dB." % (lrange_min, lrange_max))
                
        res = []
        for _ in range(3):
            slm_val = float(getText("What is the SLM reading (dB)?",
                                    title=wtitle))
            res.append(slm_val)
            time.sleep(3)
        avg = sum(res) / 3.0
        diff = abs(avg - corrected_spl)
        print("SLM Reading %g %g %g dB, average: %g dB, diff: %g dB" % (
              res[0], res[1], res[2], avg, diff))
        if diff <= calibrator_conf.get('spl_tolerance'):
            print("PASS")
        else:
            print("FAIL")
            wait("Please adjust SLM and repeat the test.")
        
        # TODO to be continued...
        

class SelfGeneratedNoiseTest616723(BaseMeasurement):
    def __call__(self):
        """Self-generated noise results BS7580, 5.5.2,  Part 1
        # dummy capacitor tolerance is +-20% of the microphone capacitor value.
        """
        wtitle = "Self-generated noise test (5.5.2 BS7580, Part 1)"
        wait("Please disconnect the microphone and connect the dummy transmitter (capacitator).",
             title=wtitle)
    
        weightings = ["A", "C", "Lin Wide"]
        for w in weightings:
            wait("Please use %s weighting." % w)
            res = []
            for _ in range(3):
                slm_val = float(getText("What is the SLM reading (dB)?",
                                        title=wtitle))
                res.append(slm_val)
                time.sleep(3)
            mean = (res[0] + res[1] + res[2]) / 3.0
            print("%s weighting. SLM measurements: %g    %g    %g    mean = %g (dB)" % (
                  w, res[0], res[1], res[2], mean))