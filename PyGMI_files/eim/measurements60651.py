"""Measurement classes loaded by SoundLevelMetersCalibration.py
Methods for ISO 60651 - BS 7580
"""
import logging
import time
from tkutils import wait, getText


class BaseMeasurement(object):
    """Common base class used in all measurements.
    """
    def __init__(self, conf, el100, wgenerator, keithley2001):
        self.conf = conf
        self.el100 = el100
        self.wgenerator = wgenerator
        self.keithley2001 = keithley2001

    def reset_instruments(self, el100=0.0):
        """Called before and after every measurement.
        """
        self.wgenerator.turn_off()
        self.el100.set(el100)
    
    def _tune_wgenerator(self, freq, target_slm, wtitle=None):
        """Tune Waveform Generator (Keysight / Agilent) voltage using a given
        frequency to achieve a target SLM measurement.
        Return voltage and attenuator values in a tuple.
        """
        self.wgenerator.set_frequency(freq=freq, volt=0.001)
        wait("Please tune first Waveform Generator voltage and then EL100 to achieve SLM %g dB." % target_slm,
             title=wtitle)
        volt = self.wgenerator.get_voltage()
        atten = self.el100.get()
        self.wgenerator.turn_off()
        return (volt, atten)

    def linearity_tolerance_limits(self, deviation, uncertainty):
        """Use to define the class in Linearity measurement.
        Ref: ISO paragraph 5.5.5.
        Return 1, 2 or 666 (foul).
        """
        total = abs(deviation) + uncertainty
        if total <= 1.1:
            return 1
        elif total <= 1.4:
            return 2
        else:
            return 666

class TimeWeighting60651(BaseMeasurement):
    """61672-3 has target SLM = max - 45 dB.
       60651 has target SLM = PIR_UPPER_LIMIT - 4
       What is the PASS/FAIL limit?
    """
    def __call__(self):
        """Execute the time weighting process and print outputs.
        """
        """Use LAFMAX SLM setting to keep SLM value in bursts.
        SEE BS7580
        """                   
        self.reset_instruments()
        target_slm = self.conf.get('linear_operating_range').get("max") - 4.0
                    
        """ FAST """
        
        wtitle = "Time Weighting (Fast)"
        wait("Please configure your SLM to FA weighting and reference range.", title=wtitle)
        (target_volt, target_atten) = self._tune_wgenerator(2000, target_slm, wtitle)
                
        res = []
        for _ in range(3):
            self.wgenerator.turn_off()
            wait("Please reset your SLM, use LAF(MAX) and start measurement.")
            self.wgenerator.start_burst(freq=2000, volt=target_volt, delay=0, count=200)
            slm_fast_burst = float(getText("What is the SLM reading (dB)?", title=wtitle))
            self.wgenerator.stop_burst()
            res.append(slm_fast_burst)
        
        print("Time Weighting Fast Continuous SLM=%g dB, attenuator %g dB" % (
              target_slm, target_atten))
        res_avg = sum(res) / 3.0
        pass_fail = self._pass_fail(self.conf.get('slm_type'), res_avg - target_slm, "F")
        print("Burst: %g %g %g dB, Average: %g %s" % (res[0], res[1], res[2], res_avg, pass_fail))
        
        """ SLOW """
        
        wtitle = "Time Weighting (Slow)"
        wait("Please configure your SLM to SA weighting.", title=wtitle)
        (target_volt, target_atten) = self._tune_wgenerator(2000, target_slm, wtitle)
                
        res = []
        for _ in range(3):
            self.wgenerator.turn_off()
            wait("Please reset your SLM, use LAF(MAX) and start measurement.")
            self.wgenerator.start_burst(freq=2000, volt=target_volt, delay=0, count=500)
            slm_fast_burst = float(getText("What is the SLM reading (dB)?", title=wtitle))
            self.wgenerator.stop_burst()
            res.append(slm_fast_burst)
        
        print("Time Weighting Slow Continuous SLM=%g dB, attenuator %g dB" % (
              target_slm, target_atten))
        res_avg = sum(res) / 3.0
        pass_fail = self._pass_fail(self.conf.get('slm_type'), res_avg - target_slm, "F")
        print("Burst: %g %g %g dB, Average: %g %s" % (res[0], res[1], res[2], res_avg, pass_fail))
                
        """ Impulse Single Burst - two test signals are used for this."""
        
        wtitle = "Time Weighting (Impulse)"
        wait("Please configure your SLM to Impulse A weighting.", title=wtitle)
        (target_volt, target_atten) = self._tune_wgenerator(2000, target_slm, wtitle)
                
        res = []
        for _ in range(3):
            self.wgenerator.turn_off()
            wait("Please reset your SLM, use LAF(MAX) and start measurement.")
            self.wgenerator.start_burst(freq=2000, volt=target_volt, delay=0, count=5)
            slm_impulse_burst = float(getText("What is the SLM reading (dB)?", title=wtitle))
            self.wgenerator.stop_burst()
            res.append(slm_impulse_burst)
        
        res2 = []
        for _ in range(3):
            self.wgenerator.turn_off()
            wait("Please reset your SLM, use LAF(MAX) and start measurement.")
            self.wgenerator.start_burst(freq=100, volt=target_volt, delay=0, count=5)
            slm_impulse_burst = float(getText("What is the SLM reading (dB)?", title=wtitle))
            self.wgenerator.stop_burst()
            res2.append(slm_impulse_burst)
        
        print("Time Weighting Impulse Continuous SLM=%g dB, attenuator %g dB" % (
              target_slm, target_atten))
        res_avg2 = sum(res2) / 3.0
        pass_fail = self._pass_fail(self.conf.get('slm_type'), res_avg - target_slm, "I1")
        print("2000Hz Burst: %g %g %g dB, Average: %g %s" % (res[0], res[1], res[2], res_avg, pass_fail))
        pass_fail = self._pass_fail(self.conf.get('slm_type'), res_avg2 - target_slm, "I2")
        print("100Hz Burst: %g %g %g dB, Average: %g %s" % (res2[0], res2[1], res2[2], res_avg2, pass_fail))
        
        self.reset_instruments()
        
    def _pass_fail(self, slm_type, diff, weighting):
        """table Page 15 of 42, The verification of SLM to BS7580.
        """
        if weighting == "F":
            diff -= 1.0
            if slm_type == 0:   
                return "PASS" if -0.5 <= diff <= 0.5 else "FAIL"
            elif slm_type == 1:
                return "PASS" if -1.0 <= diff <= 1.0 else "FAIL"
            elif slm_type == 2:
                return "PASS" if -2.0 <= diff <= 1.0 else "FAIL"
            elif slm_type == 3:
                return "PASS" if -3.0 <= diff <= 1.0 else "FAIL"
                
        elif weighting == "S":
            diff -= 4.1
            if slm_type == 0:   
                return "PASS" if -0.5 <= diff <= 0.5 else "FAIL"
            elif slm_type == 1:
                return "PASS" if -1.0 <= diff <= 1.0 else "FAIL"
            elif slm_type == 2:
                return "PASS" if -2.0 <= diff <= 2.0 else "FAIL"
            elif slm_type == 3:
                return "PASS" if -2.0 <= diff <= 2.0 else "FAIL"
                
        elif weighting == "I1":
            diff -= 8.8
            if slm_type == 0 or slm_type == 1:   
                return "PASS" if -2.0 <= diff <= 2.0 else "FAIL"
            elif slm_type == 2:
                return "PASS" if -3.0 <= diff <= 3.0 else "FAIL"
        elif weighting == "I2":
            diff -= 2.7
            if slm_type == 0 or slm_type == 1:   
                return "PASS" if -1.0 <= diff <= 1.0 else "FAIL"
            elif slm_type == 2:
                return "PASS" if -2.0 <= diff <= 2.0 else "FAIL"


class Linearity60651(BaseMeasurement):            
    def __call__(self):
        """1. The problem is that we need to set an ACPP value to get
        attenuator ~50+-10.
        If we get initial attenuator value very low or high, there will be
        a problem with other measurements.
        2. Tune attenuator until SPL = 99 (94 + 5) ...
        Uncertainty is fixed 0.2
        
        Use the same method in 60651 and 61672-3. The difference is the PASS/FAIL column
        and the Frequency=8Khz (61672-3), but its Frequency=4Khz (60651).
        
        COLUMNS
        Nominal SPL (dB)    Attn Setting (dB)    Diff ref  RefSPL    Nom Diff    Deviation    Uncertainty (dB) Class
        """
        wtitle = "Linearity (61672-3 Electrical Tests Par.14, 15)"
        self.reset_instruments(el100=3.0)
        linear_operating_range = self.conf.get('linear_operating_range')
        ref_range_lower = linear_operating_range.get('min')
        ref_point_linearity_check = 94 # FIXED value
        ref_range_upper = linear_operating_range.get('max')      
        target_slm = ref_range_upper
        
        range_upper = range(ref_point_linearity_check, int(ref_range_upper) - 4, 5) + \
                        range(int(ref_range_upper) -4, int(ref_range_upper) + 1)
        range_lower = range(ref_point_linearity_check, int(ref_range_lower) + 4, -5) + \
                        range(int(ref_range_lower) + 4, int(ref_range_lower) - 1, -1)
        logging.info("ranges")
        logging.info(range_lower)
        logging.info(range_upper)

        wait("Please configure SLM to LAF weighting at reference level range [%g, %g]." % (
             ref_range_lower, ref_range_upper))
                
        (target_volt, target_atten) = self._tune_wgenerator(4000, target_slm, wtitle)
        self.wgenerator.turn_on()
        results = []
        for idx, slm in enumerate(range_upper):
            wait("Please tune the attenuator until SLM reads %g dB." % slm)
            atten = self.el100.get()
            dif_ref_refspl = slm -  ref_point_linearity_check # TODO ???
            nom_dif = slm -  ref_point_linearity_check
            deviation = dif_ref_refspl - nom_dif
            voltage = self.keithley2001.query_voltage()
            uncertainty = 0.2
            linearity_class = self.linearity_tolerance_limits(deviation, uncertainty)
            results.append([slm, atten, dif_ref_refspl, nom_dif, voltage, linearity_class])
            # tune attenuator for next iteration
            if idx < len(range_upper) - 1:
                atten -= range_upper[idx + 1] - range_upper[idx]
            else:
                # do not set the attenuator in the last iteration, move to next
                break
            if atten < 0.0:
                wait("ERROR! Attenuator cannot get a negative value %g. Restarting linearity testing." % atten)
                self.linearity()
            self.el100.set(atten)
            
        for idx, slm in enumerate(range_lower):
            wait("Please check & tune the attenuator to make sure that SLM reads %g dB." % slm)
            atten = self.el100.get()
            dif_ref_refspl = slm -  ref_point_linearity_check # TODO ???
            nom_dif = slm -  ref_point_linearity_check
            deviation = dif_ref_refspl - nom_dif
            voltage = self.keithley2001.query_voltage()
            uncertainty = 0.2
            linearity_class = self.linearity_tolerance_limits(deviation, uncertainty)
            results.append([slm, atten, dif_ref_refspl, nom_dif, voltage, linearity_class])
            # tune attenuator for next iteration
            if idx < len(range_lower) - 1:
                atten += range_lower[idx] - range_lower[idx + 1]
            else:
                # do not set the attenuator in the last iteration, move to next
                break
            
            if atten > 99.99:
                wait("ERROR! Attenuator cannot get a value over 99.99, %g. Restarting linearity testing." % atten)
                self.linearity()
            self.el100.set(atten)           
        print("Linearity Test")
        print("Nominal SPL  Attn Setting  Diff re RefSpl  Nom Diff  Voltage Class")
        print("    (dB)        (dB)          (dB)          (dB)      (V)         ")
        for row in results:
            print("    %.1f        %.2f        %.2f        %.2f       %.2f        %d" % (
                  row[0], row[1], row[2], row[3], row[4], row[5]))
        
        # Proceed only if there are many level ranges
        level_ranges = self.conf.get('level_ranges')
        if len(level_ranges) <= 1:
            print("Linearity check complete.")
            self.reset_instruments()
            return
        
        def _print_level(upper, lower, at1, at2, at3, at4, dvm_rdg):
            """TODO this works only if upper > 94 > lower
            """
            print("Range | Nominal SPL | Attn Setting | Diff re RefSpl | Nom Diff | Dvm Rdg | Pass/Fail")
            print("         (dB)       |   (dB)       |   (dB)         |   (dB)      (mV)")
            
            if upper >= 94:
                nom_diff1 = upper - 2 - 94
                nom_diff2 = 0.0
                nom_diff3 = 0.0
                nom_diff4 = lower + 2 - 94
                
                # The threshold depends on the SLM class
                uncertainty = 0.2
                class1 = self.linearity_tolerance_limits(nom_diff1 - (at1 - at3), uncertainty)     
                class2 = self.linearity_tolerance_limits(nom_diff2 - (at1 - at2), uncertainty)
                class3 = self.linearity_tolerance_limits(nom_diff3 - (at1 - at1), uncertainty)
                class4 = self.linearity_tolerance_limits(nom_diff4 - (at1 - at4), uncertainty)
                
                print(" %.1f | %.1f     | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                    upper, upper-2.0, at3, at1 - at3, nom_diff1, dvm_rdg, class1 ))
                print("  0.0 |  94.0   | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                      at2, at1 - at2, nom_diff2, dvm_rdg, class2 ))
                print("  0.0 | Ref       | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                      at1, at1 - at1, nom_diff3, dvm_rdg, class3 ))
                print("  0.0 | %.1f      | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                      lower+2.0, at4, at1 - at4, nom_diff4, dvm_rdg, class4 ))
            else:
                nom_diff1 = 94 - (upper - 2)
                nom_diff3 = 0.0
                nom_diff4 = lower + 2 - 94
                
                # The threshold depends on the SLM class TODO
                uncertainty = 0.2
                class1 = self.linearity_tolerance_limits(nom_diff1 - (at1 - at3), uncertainty)            
                class3 = self.linearity_tolerance_limits(nom_diff3 - (at1 - at1), uncertainty)
                class4 = self.linearity_tolerance_limits(nom_diff4 - (at1 - at4), uncertainty)
                
                print(" %.1f | %.1f     | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                    upper, upper-2.0, at3, at1 - at3, nom_diff1, dvm_rdg, class1 ))
                print("  0.0 | Ref       | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                      at1, at1 - at1, nom_diff3, dvm_rdg, class3 ))
                print("  0.0 | %.1f      | %.2f        | %.2f           | %.2f  | %.2f  | %s" % (
                      lower+2.0, at4, at1 - at4, nom_diff4, dvm_rdg, class4 ))
                
        # Document reference: New IEC Standards and Periodic Testing of Sound
        # Level Meters. Section 6.9, standard 61672-3 clause 15.2 15.3 15.4
        if self.conf.get("standard") == "60651":
            freq = 4000        
        elif self.conf.get("standard") == "61672-3":
            freq = 8000   
        
        # We skip the first level range (reference) because we have already
        # checked it before in the linearity process.
        print("Other Ranges Linearity Test")
        for lrange in level_ranges[1:]:
            # If 94 is within range.
            if lrange[0] > 94 > lrange[1]:
                wait("Please configure SLM to A weighting at level range [%g, %g]." % (lrange[0], lrange[1]))
                self.el100.set("01.00")
                # Tune function generator and attenuator to achieve SLM value = (max upper value - 2)
                # NOTE: Must keep ref_volt, ref_atten for later comparisons!
                (ref_volt, ref_atten) = self._tune_wgenerator(freq, lrange[0] - 2, wtitle)
                wait("Please configure SLM to A weighting at reference level range [%g, %g]." % (
                    ref_range_lower, ref_range_upper))
        
                atten_dif = lrange[0] - 2 - 94  # 94 is the fixed reference value
                self.el100.set(ref_atten + atten_dif)
                self.wgenerator.turn_on()
                wait("Please tune the attenuator manually to achieve SLM 94 dB.")
                at1 = self.el100.get()
                
                wait("Please configure SLM to A weighting at level range [%g, %g]." % (lrange[0], lrange[1]))
                wait("Please tune the attenuator manually to achieve SLM 94 dB")
                at2 = self.el100.get()
                upper_target = lrange[0] - 2
                self.el100.set(at2 - (upper_target - 94))
                wait("Please tune the attenuator manually to achieve SLM %g dB" % upper_target)
                at3 = self.el100.get()
                                
                lower_target = lrange[1] + 2
                self.el100.set(at2 + (94 - lower_target))
                wait("Please tune the attenuator manually to achieve SLM %g dB" % lower_target)
                at4 = self.el100.get()
            # If 94 is outside range (e.g. range is [90,20]
            else:
                wait("Please configure SLM to A weighting at level range [%g, %g]." % (lrange[0], lrange[1]))
                self.el100.set("01.00")
                # Tune function generator and attenuator to achieve SLM value = (max upper value - 2)
                # NOTE: Must keep ref_volt, ref_atten for later comparisons!
                (ref_volt, ref_atten) = self._tune_wgenerator(freq, lrange[0] - 2, wtitle)
                wait("Please configure SLM to A weighting at reference level range [%g, %g]." % (
                    ref_range_lower, ref_range_upper))
        
                atten_dif = 94 - (lrange[0] - 2)  # 94 is the fixed reference value
                self.el100.set(ref_atten - atten_dif)
                self.wgenerator.turn_on()
                wait("Please tune the attenuator manually to achieve SLM 94 dB.")
                at1 = self.el100.get()   
                
                wait("Please configure SLM to A weighting at level range [%g, %g]." % (lrange[0], lrange[1]))          
                at2 = 0.0  # not used - we don't do anything about it.                                
                upper_target = lrange[0] - 2
                atten_plus = 94 - upper_target
                self.el100.set(ref_atten + atten_plus)
                wait("Please tune the attenuator manually to achieve SLM %g dB" % upper_target)
                at3 = self.el100.get()
                        
                lower_target = lrange[1] + 2
                atten_minus = 94 - lower_target
                self.el100.set(ref_atten + atten_minus)
                wait("Please tune the attenuator manually to achieve SLM %g dB" % lower_target)
                at4 = self.el100.get()
                                                       
            _print_level(upper=lrange[0], lower=lrange[1], at1=at1, at2=at2,
                         at3=at3, at4=at4, dvm_rdg=ref_volt)              
        
        self.reset_instruments()       


class FrequencyWeighting60651(BaseMeasurement):
    def __call__(self):
        """Initial el100 value is not fixed. It is calculated by SLM manual values.
        Max linearity range (e.g. 140) - 45 (fixed by standard 61672)
        We run the frequency weighting 3 times (A, C, Z).
        We do NOT change anything in our code/process, only SLM device settings
        change.
        Reference SPL comes from the manufacturer.
        
        Use the same method for ISO 60651 and 61672-3.
        """
        self.reset_instruments(el100=99.00)
        linear_operating_range = self.conf.get("linear_operating_range")
        self.wgenerator.set_frequency(1000.0, volt=0.5)
        self.wgenerator.turn_on()
        
        spl_aim = linear_operating_range.get("max") - 45
        
        wait("Please set your Sound Level Meter to A weighting and tune the attenuator until SLM value is %g." % spl_aim)
                        
        self.el100_ref_value = self.el100.get() 
        
        print("Waveform Generator %g Hz, %g V, attenuator %g dB, SLM %g dB" % (
              1000.0, 0.5, self.el100_ref_value, spl_aim))
        
        """ISO61672-1 IEC:2002, Table 2, Page 33.
        Frequency_weighting = 'A', 'C' or 'Z'
        NOTE that there is a standard uncertainty budget = 0.21
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
                self.wgenerator.set_frequency(freq, volt=0.5)
                slm_reading = float(getText("Frequency = %g. What is the SLM reading (dB)?" % freq))    
                overall_response = slm_reading + case_corrections[freq] + windshield_corrections[freq]
    
                expected = spl_aim + table_freq_weightings[freq][weighting]
                deviation = round(slm_reading - expected + windshield_corrections[freq] + case_corrections[freq], 2)
                if(deviation >= 0.0):
                    deviation += 0.21
                else:
                    deviation -= 0.21
                if tolerance_limits[freq][1]["min"] <= deviation <= tolerance_limits[freq][1]["max"]:
                    slm_class = 1
                elif tolerance_limits[freq][2]["min"] <= deviation <= tolerance_limits[freq][2]["max"]:
                    slm_class = 2
                else:
                    slm_class = 666
                
                row = [freq, self.el100_ref_value, slm_reading, windshield_corrections[freq],
                       case_corrections[freq], overall_response, expected, deviation, slm_class]
                print(row)
                results.append(row)
                
            print("Frequency Weighting %s Results" % weighting)
            print("Frequency    Attn    Slm reading    Windshield corr    Case corr    Overall response  Expected Deviation    Class")
            print("   (Hz)      (dB)       (dB)             (dB)            (dB)            (dB)           (dB)     (dB)")
            for row in results:
                print("%6.1f      %.2f       %.2f          %.2f            %.2f            %.2f        %.2f        %.2f       %d" % (
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        self.reset_instruments()


class PeakResponse60651(BaseMeasurement):
    def __call__(self):
        """TODO peak response.
        """
        wtitle = "Peak Response, ISO61670"
        level_ranges = self.conf.get('level_ranges')
        upper_ref_level_range = level_ranges[0][0]
        lower_ref_level_range = level_ranges[0][1]
        weighting = "A"
        wait("Please set your Sound Level Meter REF level range (%g, %g) and %s weighting and press any key to continue." % (
             upper_ref_level_range, lower_ref_level_range, weighting), wtitle)
       
        slm_aim = upper_ref_level_range - 1.0        
        (volt, atten) = self._tune_wgenerator(2000, slm_aim, wtitle)
                
        self.wgenerator.set_frequency(2000, volt, shape='SIN')
        self.wgenerator.turn_on()
        slm_sin = float(getText("What is the SLM reading (dB)?"))
        self.wgenerator.turn_off()
        wait("Plase reset your SLM.")
        
        self.wgenerator.set_frequency(2000, volt, shape='RECT')
        self.wgenerator.turn_on()
        slm_square = float(getText("What is the SLM reading (dB)?"))
        self.wgenerator.turn_off()
                        
        # TODO for all types of instrument the test pulse shall produce
        # an indication no more than 2 dB below the indication
        # for the reference pulse
        print("Shape: SIN, SLM %g dB" % slm_sin)
        print("Shape: SQUARE, SLM %g dB" % slm_square)
        diff = slm_square - slm_sin
        pass_fail = "PASS" if abs(diff) < 2.0 else "FAIL"
        print("Difference: %g %s" % (diff, pass_fail))


class TimeAveraging60651(BaseMeasurement):
    def __call__(self):
        """Time averaging TODO check with Yiannis
        """
        slm_type = self.conf.get('slm_type')
        self.reset_instruments(el100=99.00)
        slm_target = 90.0
        wait("Please configure your SLM to use Leq.")
        self.wgenerator.set_frequency(4000, volt=1.0)
        wait("Please configure the attenuator value so that SLM reads %g dB." % slm_target)
        ref_attenuation = self.el100.get()
        wait("Please reset your SLM.")
                        
        # TODO test frequency of 4kHz continuous
        self.wgenerator.set_frequency(4000, volt=1.0)
        slm_val1 = float(getText("What is the SLM reading (dB)?"))
        self.wgenerator.turn_off()
        wait("Please reset your SLM.")
        print("Generator: 4Khz, 1V, SLM Leq value=%g" % slm_val1)
        
        # 1ms toneburst for 60s
        self.wgenerator.start_burst(freq=2000, volt=1.0, delay=0, count=1)
        time.sleep(60)
        self.wgenerator.stop_burst()
        slm_val2 = float(getText("What is the SLM reading (dB)?"))
        diff2 = slm_val2 - slm_val1
        wait("Please reset your SLM.")
        print("Generator: 4Khz, 1V, burst 1ms, 60sec, SLM Leq value=%g, diff=%g" % (slm_val2, diff2))
        if slm_type == 0:
            print "PASS " if -0.5 <= diff2 <= 0.5 else "FAIL"
        elif slm_type == 1:
            print "PASS " if -1.0 <= diff2 <= 1.0 else "FAIL"
        else:
            print "PASS " if -1.5 <= diff2 <= 1.5 else "FAIL"
    
        # The amplitude of the continuous signal is 30 dB below the upper limit.
        
        # 1ms toneburst for 300s
        self.wgenerator.start_burst(freq=2000, volt=1.0, delay=0, count=1)
        time.sleep(300)
        self.wgenerator.stop_burst()
        slm_val3 = float(getText("What is the SLM reading (dB)?"))
        diff3 = slm_val3 - slm_val1
        wait("Please reset your SLM.")
        print("Generator: 4Khz, 1V, burst 1ms, 300sec, SLM Leq value=%g, diff=%g" % (slm_val3, diff3))
        print "PASS " if -1.0 <= diff3 <= 1.0 else "FAIL"
        
        # The amplitude of the continuous signal is 40 dB below the upper limit.


class RmsAccuracyAndOverload60651(BaseMeasurement):
    def __call__(self):
        # TODO run with Yiannis
        
        # TODO page 16 of 42 The verification of SLM to BS7580
        # The toneburst consists of 11 cycles of a sine wave of frequency 2 kHz
        # with a repetition frequency of 40 Hz and having an RMS level which is
        # identical to that of the continuous sine wave signal.
        self.reset_instruments()
        #lrange = self.conf.get('least_sensitive_level_range')
        #upper_range = lrange[0]
        #lower_range = lrange[1]
        upper_range = 120
        lower_range = 40

        target_slm = upper_range - 2
               
        wtitle = "RMS Accuracy and Overload"                
        wait("Please set your Sound Level Meter REF level range (%g, %g) and A weighting and press any key to continue." % (
             upper_range, lower_range), title=wtitle)

        self.el100.set(20.00) # Must start with a high value and the decrease it
        slm_initial = upper_range - 1
        (target_volt, atten_positive) = self._tune_wgenerator(2000, target_slm, wtitle)
        
        atten = atten_positive
        step = 0.5
        switch_step = True
        results = []
        while(True):
            self.wgenerator.start_burst(freq=2000, volt=target_volt, delay=0, count=11)
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
                    myclass = 1 if -1.8 <= slm_diff <= 1.8 else 2   # TODO change this
                    results.append((slm_initial, atten_positive, slm_overload,
                                    atten_overload, slm_diff, uncertainty, myclass))
                    break
                    # TODO BUG not breaking here.
            else:                         
                atten -= step
            self.wgenerator.stop_burst()
            self.el100.set(atten)

        # reducing the signal level by 1 dB
        atten -= 1.0
        self.wgenerator.start_burst(freq=2000, volt=target_volt, delay=0, count=11)
        slm_overload = float(getText("What is the current SLM value?"))
        slm_diff = slm_overload - slm_initial
        uncertainty = 0.2
        myclass = 1 if -1.8 <= slm_diff <= 1.8 else 2   # TODO change this
        results.append((slm_initial, atten_positive, slm_overload,
                        atten_overload, slm_diff, uncertainty, myclass))
        self.wgenerator.stop_burst()
        
        # reducing the signal level by a further 3 dB
        atten -= 3
        self.wgenerator.start_burst(freq=2000, volt=target_volt, delay=0, count=11)
        slm_overload = float(getText("What is the current SLM value?"))
        slm_diff = slm_overload - slm_initial
        uncertainty = 0.2
        myclass = 1 if -1.8 <= slm_diff <= 1.8 else 2   # TODO change this
        results.append((slm_initial, atten_positive, slm_overload,
                        atten_overload, slm_diff, uncertainty, myclass))
        self.wgenerator.stop_burst()

        print("initial SLM | atten | overload SLM | atten | diff SLM | uncertainty | class")
        for row in results:
            print("   %.2f     %.2f      %.2f      %.2f       %.2f       %.2f       %d" % (
                row[0], row[1], row[2], row[3], row[4], row[5], row[6]))       
    
        self.reset_instruments()
        
        
class PulseRangeSoundExposureLevelAndOverload60651(BaseMeasurement):
    def __run__(self):
        """Continuous level set up to 50dB
        50 dB not attenable therefore set up to 50.1 dB
        Attenuator reading = 58.55
        Channel 1 reconnect and adjusted to read 108 dB
            40 cycle bursts applied. Slm set to Leq and reset.
        SLM reading after 10s = 78.2 78.2 78.2 dB
        Nominal Reading = 78 dB
        """
        wtitle = "Pulse Range Sound Exposure Level & Overload (Subclauses 5.5.10, 5.5.11 and 5.5.12 of BS 7580: Part 1)."
        target_slm = 50
        (target_volt, target_atten) = self._tune_wgenerator(1000, target_slm, wtitle)
        # TODO what reconnect & adjusted means?
        # TODO 
        
        """Sound exposure test
        40 cycle burst applied to SLM. set to SEL and reset.
        SLM reading = 87.8 87.8 87.8
        Nominal Reading = 88 dB
        """
        wait("Please set your SLM to SEL and reset.")
        self.wgenerator.start_burst(freq=1000, volt=target_volt, delay=0, count=40)
        res = []
        for _ in range(3):
            slm_val = float(getText("What is the SLM reading (dB)?", title=wtitle))
            res.append(slm_val)
            time.sleep(3)
        self.wgenerator.stop_burst()
        slm_mean = (res[0] + res[1] + res[2]) / 3.0
        
        print("%d cycle burst applied to SLM.")
        print("SLM readings: %g %g %g dB" % ( res[0], res[1], res[2]))
        print("Nominal Reading = %g dB" % 9999)
        # TODO what is the nominal reading?
        
        """Overload test (Integrating Mode)
        Output level of PM5138A adjusted until overload, the decreased by 1 dB.
        Corresponding continuous reading = 120.4 dB
        4 cycle burst applied, SLM set LEQ and reset
        SLM reading after 10 s = 80.7 80.7 80.7 dB
        Nominal Reading = 80.4 dB)
        """