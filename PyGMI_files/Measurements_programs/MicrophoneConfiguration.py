import logging
import math
import numpy
import pprint
import threading
import time
from Tkinter import *
import tkMessageBox
import winsound

#from microphone_uncertainties import attenuator_uncertainty


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
    msg = msgBox.getString()   
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
        m=self.mainapp              #a shortcut to the main app, especially the instruments
        f=self.frontpanel           #a shortcut to frontpanel values
        reserved_bus_access=self.GPIB_bus_lock     #a lock that reserves the access to the GPIB bus
        
        #out = self.calculate_uncertainties([{'SPL': 93.99}, {'SPL':93.99}, {'SPL':93.99}], {})
        #print(out)
        #sys.exit(0)
        
        #val = self.corrected_spl(3.944, 43.85, -31.006, 1.9712, 1.973)  
        #print("CORRECTED SPL", val)
        #sys.exit(0)
        #t = self.uncorrected_sound_pressure_level(Vins=1.9, A=43.84, M=94)
        #print(t)
        #sys.exit(0)
                
        logging.info("init all instruments")
        self.keithley2001 = m.instr_1   # GBIP0::16
        self.racaldana = m.instr_2      # GBIP0::14
        self.agilent3350A = m.instr_3   # GBIP0::20
        self.kh6880A = m.instr_4        # GBIP0::1
        self.bk2636 = m.instr_5         # GBIP0::4
        self.dpi141 = m.instr_6         # GBIP0::2
        self.el100 = m.instr_7          # GBIP0::3
                
        # debugging script
        # agilent on
        # kh on
        # racal on
        # keithley 2001 must read channel 3 AC, value 1 V
        #self.agilent3350A.turn_on()
        #v_test = self.keithley2001.scan_channel(3, "VOLT:AC")
        #print(v_test)    
        #sys.exit(0)
           
        SPL_standard = []
        SPL_device = []
        
        self.el100.set("99.99")
        self.agilent3350A.turn_off()
        
        # TODO
        # ASK Microphone type
        # LOAD configuration from C:\accoustics-configuration\mic-name.yaml
        #    what settings?
        #        
        # ASK calibrator type
        # LOAD configuration from C:\accoustics-configuration\calibrator-name.yaml
        #    what settings?
        #        Kpv
        #        ??
        
        t1 = float(getText("Initial temperature (oC)").strip())
        rh1 = float(getText("Initial humidity (%)").strip())
        p1 = self.dpi141.read() 
        vpol1 = self.keithley2001.scan_channel(4, "VOLT:DC")[0]
        self.check_temperature(t1)
        self.check_humidity(rh1)
        self.check_pressure(p1)
        self.check_vpol(vpol1)
        
        self.calibrator_nominalevel = int(getText("Calibrator Nominal Level (94, 104 or 114dB)").strip())
        self.micsensitivity = float(getText("Microphone Sensitivity (check certificate, e.g. -26.49)").strip())
        self.bk2636.decide_set_gain(self.calibrator_nominalevel, self.micsensitivity)
        
        for _ in range(1):  # TODO 5           
            self.stop_switch_instrument("Reference Standard")
            # delay time necessary for calibrator
            print("Wait for 20 sec")
            time.sleep(20)
            res = self.measure_SPL("Reference Standard")
            SPL_standard.append(res)
            
            #self.stop_switch_instrument("Customer Device")
            #time.sleep(5)
            #res = self.measure_SPL("Customer Device") 
            SPL_device.append(res)               
        
        # final env conditions
        t2 = float(getText("Final temperature (oC)").strip())
        rh2 = float(getText("Final humidity (%)").strip())
        p2 = self.dpi141.read()
        vpol2 = self.keithley2001.scan_channel(4, "VOLT:DC")[0]
        
        self.check_temperature(t2)
        self.check_humidity(rh2)
        self.check_pressure(p2)
        self.check_vpol(vpol2)
        
        env = dict(temperature=(t1+t2)/2.0,
                   relative_humidity=(rh1+rh2)/2.0,
                   pressure=(p1+p2)/2.0,
                   polarising_voltage=(vpol1+vpol2)/2.0)
        
        standard_uncertainty = self.calculate_uncertainties(SPL_standard, env)
        device_uncertainty = self.calculate_uncertainties(SPL_device, env)       
                
        self.print_results(env, SPL_standard, SPL_device, standard_uncertainty,
                           device_uncertainty)               
    
    def measure_SPL(self, device_name):
        """"Big process that is repeated 5 times for working standard
        and customer device. The final output is a dict with all measurements.
        """               
        self.agilent3350A.turn_off()
       
        # Read Total Harmonic Distortion (THD) from Krohn Hite. This is used in
        # the final result
        kh_list1 = self.kh6880A.read(times=10, delay=1.99)
        kh_avg1 = sum(kh_list1) / len(kh_list1)
        print("AVG DISTORTION", kh_list1)
    
        # check Keithley2001 DC & CURR stability/fluctuation. MA o/p (V) is vmic 
        dc_volt = self.keithley2001.scan_channel(5, "VOLT:DC", times=20, interval=0.99)
        self._check_stability(dc_volt)
        vmic = sum(dc_volt) / len(dc_volt)
        
        wait("Stop %s, press any key to continue..." % device_name)
                
        # start agilent3350A, send 6V peak to peak, freq 1000Hz, SINE waveform.
        # the attenuator is adjusted until the voltage matches (to 0.005 db) the
        # output of the calibrator (VmicAmpl(ch5) - VinsertAmpl(ch5))           
        # Vdev = Vmic
        # Vsys = Vins
        # atten#=100.0# - micsensitivity# - nomlevel#
        # micsensivity input variable by user (certificate). e.g. value = -26.49
        # calibrator nominal level e.g. value = 94
        self.agilent3350A.turn_on()        
        atten = 100.0 - self.micsensitivity - self.calibrator_nominalevel
        good_consec = 0
        vins = 0.0
        while good_consec < 2:
            attenuator_str = "%05.2f" % atten
            self.el100.set(attenuator_str)
            vins = self.keithley2001.scan_channel(5, "VOLT:DC")[0]
            print("atten keithley channel 5 DC", vins, "vmic", vmic)
            # MA o/p (V) is vins
                        
            # convert to dB and check value < 0.005 two times for success
            attenerror = 20.0 * math.log10(vmic / vins)
            if abs(attenerror) <= 0.005:
                good_consec += 1
                print("SUCCESS", attenerror)
            else:
                print("ERROR", attenerror)
                atten -= attenerror
                time.sleep(5)
                
        # measure Vins voltage (ch3) keythley
        dc_volt = self.keithley2001.scan_channel(3, "VOLT:AC", times=20, interval=0.99)
        vins_source3 = sum(dc_volt) / len(dc_volt)
        
        rd_avg = self.racaldana.read_average(times=20, delay=1.99)
        logging.info("Racal Dana read %g", rd_avg)
        # Racal Dana values must be around 1000 Hz +-10%
        if rd_avg < 900.0 or rd_avg > 1100.0:
            wait("Critical Error! Racal Dana value outside range: %g. Terminating program." % rd_avg)
            sys.exit(0)
            
        # Get Total Harmonic Distortion value for 2nd time from Krohn Hite (kh6880A)
        # this kh_list2 is used ONLY to validate kh_list1 not in the results!!!
        kh_list2 = self.kh6880A.read(times=10, delay=1.99)      
        kh_avg2 = sum(kh_list2) / len(kh_list2)
        
        thd = sum(kh_list1) / len(kh_list1)
                
        SPL = self.uncorrected_sound_pressure_level(vins_source3, atten,
                                                    self.micsensitivity)    # , vmic, vins)        
        self.agilent3350A.turn_off()
        
        return dict(
            attenuation=atten,
            thd=thd,
            krohn_hite=kh_avg1,
            racal_dana=rd_avg,
            SPL=SPL,
            Vmic=vmic,      # MA_op first
            Vins=vins,      # MA_op second
            IV=vins_source3
        )
        
    def corrected_spl(self, Vins3, A, M, Vmic, Vins5):
        
        SPL = (20.0*math.log10(Vins3)) - A + (20.0 * math.log10(Vmic)) -\
              (20.0*math.log10(Vins5)) - M - (20.0*math.log10(0.00002)) # - pressure correction
        return SPL
        
        
    def uncorrected_sound_pressure_level(self, Vins, A, M):
        """SPL calculation. Params:
        Vins: measured insert voltage
        A: attenuation (dB)
        M: sensitivity (dB re 1 VPa-1)
        Output: SPL
        """
        print("Vins", Vins, "A", A, "M", M)
        
        SPL = (20.0*math.log10(Vins)) - (20.0*math.log10(0.00002)) -A - M
        return round(SPL, 3)
    
    def stop_switch_instrument(self, device):
        wait("Please connect and turn on the %s." % device)
    
    def _keithley_wait_until_dc_voltage(self, limit=0.5):
        """"Read DC voltage from keithley2001 until value > 0.5V.
        If not, sleep for 1 sec and retry.
        """      
        self.keithley2001.set_measurement_mode("DC")
        while(True):
            dc_voltage = self.keithley2001.query_voltage_average()
            if dc_voltage > 0.5:
                break
            time.sleep(1)
    
    def _check_stability(self, values):
        """Input is list of floats. If last/first value < 0.7, faulty reading.
        Exit with an error"""
        if values[-1] / values[0] < 0.7:
            logging.error("Fatal problem with measurement stability.")
            logging.error(values)
            sys.exit(0)
        # TODO return and save stability (fluctuation)
            
    def check_temperature(self, temp):
        if not 20.0 <= temp <= 26:
            msg = "Temperature %g outside preferred range of 23+-3 oC." % temp
            logging.error(msg)
            wait(msg)
                        
    def check_humidity(self, rh):
        if not 30.0 <= rh <= 70.0:
            msg = "Humidity %g outside preferred range of 50+-20%%." % rh
            logging.error(msg)
            wait(msg)
    
    def check_pressure(self, pre):
        if not 1003.0 <= pre <= 1023.0:
            msg = "Pressure %g outside preferred range of 1013+-10."% pre
            logging.error(msg)
            wait(msg)
    
    def check_vpol(self, v):
        if not 198.0 <= v <= 202.0:
            msg = "Polirization V %g outside preferred range of 200+-2V." % v
            logging.error(msg)
            wait(msg)
            
    def calculate_fluctuation(self, v_list):
        """Calculate fluctuation for a list of values.
        """
        mean_val = sum(v_list) / len(v_list)
        max_val = max(v_list)
        min_val = min(v_list)
        highest_fluctuation = 20 * math.log10(max_val / mean_val)
        lowest_fluctuation = 20 * math.log10(min_val/ mean_val)
        if abs(highest_fluctuation) > abs(lowest_fluctuation):
            return highest_fluctuation
        else:
            return lowest_fluctuation
    
    def calculate_uncertainties(self, measurements, env):
        IVu = self.voltmeter_uncertainty(1.0005)    # value from certificate
        IVe = self.voltmeter_uncertainty(1.0003)    # value from certificate
        
        avg_attenuation = sum([row['attenuation'] for row in measurements]) / len(measurements)
        Au = self.attenuator_uncertainty(avg_attenuation)
        Ae = self.attenuator_error(avg_attenuation)
        
        Mu = 0.05   # value from certificate
        Mp = 0.01   # table page 24 of 42
        Mt = 0.007  # table page 25 of 42
        MM = 0.005  # STANDARD page 25
        Kpv = 0.0004    # BK2636 polarization voltage certificate
        Kp = 0.01  # Page 26 of 42
        Kmv = 0.0
        SPLr = 0.005
        
        sqrt3 = math.sqrt(3)
        
        u_IVu = round(IVu / 2.0, 4)
        u_IVu2 = pow(u_IVu, 2)
        u_IVe = round(IVe / sqrt3, 4)
        u_IVe2 = pow(u_IVe, 2)
        u_Au = round(Au / 2.0, 4)
        u_Au2 = pow(u_Au, 2)
        u_Ae = round(Ae / sqrt3, 4)
        u_Ae2 = pow(u_Ae, 2)
        u_Mu = round(Mu / 2.0, 4)
        u_Mu2 = pow(u_Mu, 2)
        u_Mp = round(Mp / sqrt3, 4)
        u_Mp2 = pow(u_Mp, 2)
        u_Mt = round(Mt / sqrt3, 4)
        u_Mt2 = pow(u_Mt, 2)
        u_MM = round(MM / sqrt3, 4)
        u_MM2 = pow(u_MM, 2)
        u_Kpv = round(Kpv / sqrt3, 4)
        u_Kpv2 = pow(u_Kpv, 2)
        u_Kp = round(Kp / sqrt3, 4)
        u_Kp2 = pow(u_Kp, 2)
        u_Kmv = round(Kmv / sqrt3, 4)
        u_Kmv2 = pow(u_Kmv, 2)
        u_SPLr = round(SPLr / sqrt3, 4)
        u_SPLr2 = pow(u_SPLr, 2)
        
        spls = numpy.array([row['SPL'] for row in measurements])
        spl_repeatability = numpy.std(spls) 
        # CHECK spl_repeatability = 0.0045
        spl_repeatability2 = pow(spl_repeatability, 2)
        #SPL_avg = sum(item['SPL'] for item in measurements) / len(measurements)
        
        total = u_IVu2 + u_IVe2 + u_Au2 + u_Ae2 + u_Mu2 + u_Mp2 + u_Mt2 + u_MM2 + u_Kpv2 +\
                u_Kp2 + u_Kmv2 + u_SPLr2 + spl_repeatability2
        total = math.sqrt(total)
        
        pcorr = 0.0 # TODO later YIANIS 
        vcorr = -20.0 * math.log10(env['polarising_voltage'] / 200.0)
        pvcorr = round(pcorr + vcorr, 3)
        
        frequencies = numpy.array([item['racal_dana'] for item in measurements])
        u_frequency = numpy.std(frequencies) * 2.0
        
        #u_SPL = IVu + IVe - 20*math.log10(0.00002) - Au + Ae - Mu + Mp + Mt +\
        #        MM + Kpv + Kp + Kmv + SPLr 
              
        out = dict(
            IVu=u_IVu,
            IVe=u_IVe,
            Au=u_Au,
            Ae=u_Ae,
            Mu=u_Mu,
            Mp=u_Mp,
            Mt=u_Mt,
            MM=u_MM,
            Kpv=u_Kpv,
            Kp=u_Kp,
            SPLr=u_SPLr,
            spl_repeatability=spl_repeatability,
            total=total,
            
            u_total=total * 2.0,
            u_thd=u_Au2 * 2.0,
            u_SPL=spl_repeatability2 * 2.0,
            u_type_A=spl_repeatability2 * 2.0,
            u_frequency=u_frequency,
            pvcorr=pvcorr
            )
        return out
     
    def combined_uncertainty(self, IVu, IVe, Au, Ae, Mu, Mp, Mt, MM, Kpv,
                             Kp, Kmv, SPLr, spl):
        sqrt3 = math.sqrt(3)

        u_IVu = math.pow(IVu / 2.0, 2)
        u_IVe = math.pow(IVe / sqrt3, 2)
        u_Au = math.pow(Au / 2.0, 2)
        u_Ae = math.pow(Ae / math.sqrt(3), 2)
        u_Mu = math.pow(Mu / 2.0, 2)
        u_Mp = math.pow(Mp / sqrt3, 2)
        u_Mt = math.pow(Mt / sqrt3, 2)
        u_MM = math.pow(MM / sqrt3, 2)
        u_Kpv = math.pow(Kpv / sqrt3, 2)
        u_Kp = math.pow(Kp / sqrt3, 2)
        u_Kmv = math.pow(Kmv / sqrt3, 2)
        u_SPL = IVu + IVe - 20*math.log10(0.00002) - Au + Ae - Mu + Mp + Mt +\
                MM + Kpv + Kp + Kmv + SPLr 
        u_SPLr = math.pow(SPLr / sqrt3, 2)       
    
        total = u_IVu + u_IVe + u_Au + u_Ae + u_Mu + u_Mp + u_Mt + u_MM + u_Kpv +\
                u_Kp + u_Kmv + u_SPLr
        return dict(
            IVu=u_IVu,
            IVe=u_IVe,
            Au=u_Au,
            Ae=u_Ae,
            Mu=u_Mu,
            Mp=u_Mp,
            Mt=u_Mt,
            MM=u_MM,
            Kpv=u_Kpv,
            Kp=u_Kp,
            Kmv=u_Kmv,
            SPL=u_SPL,
            SPLr=u_SPLr,
            total=round(math.sqrt(total), 3)   
            )
    
    def voltmeter_uncertainty(self, val):
        """Keithley2001
        Get value from Voltmeter certificate uncertainty.
        """
        return 20 * math.log10(val)

    def voltmeter_error(self, val):
        """Keithley2001
        """
        return self.voltmeter_uncertainty(val)

    def attenuator_uncertainty(self, value):
        """input: MSD (tens) of attenuator setting value (first digit)
        output: Au (dB) (0.01 - 0.06)
        """
        attenuator_str = "%05.2f" % value
        msd = int(attenuator_str[0])
        if msd == 0:
            return 0.01
        elif msd == 1:
            return 0.02
        elif msd == 2:
            return 0.03
        elif msd == 3:
            return 0.04
        elif msd == 4:
            return 0.05
        elif msd == 5:
            return 0.06
    
    def attenuator_error(self, value):
        """Error in attenuator reading (dB) for different frequency ranges.       
        frequency = Agilent frequency = 1000 (ALWAYS)
        table 15.5, page 23 of 42, only the second column applies (250Hz to 2kHz)
        
        0.004 uncertainty is STANDARD in all cases (LSD uncertainty).
        We add to this according to MSD (first digit of attenuator value)
        """
        attenuator_str = "%05.2f" % value
        msd = int(attenuator_str[0])
        if msd == 0:
            return 0.004
        elif msd == 1 or msd == 2:
            return 0.004 + 0.004
        elif msd == 3:
            return 0.005 + 0.004
        elif msd == 4 or msd == 5:
            return 0.005 + 0.004
        elif msd == 6:
            return 0.006 + 0.004
    
    def microphone_est_maximum_error(self, mic_type, freq, spr, Mp):
        """mic_type: Microphone type
        freq: Frequency range (Hz)
        spr: Static pressure range (kPa)
        Mp: (dB)
        """
        return 0.01
    
    def coverage_factor(self, niterns, urfreq, ufreq, k_necessary):
        return 0.1

    def print_results(self, env, SPL_standard, SPL_device, standard_u, device_u):  
        # TODO IV (V) double value!!
        # TODO Freq unc = 0.00 there must be a small value here
        # TODO SPL wrong -> depends on IV (V)
        header = "Freq(Hz)    MA o/p (V)    MA o/p (V)    IV (V)    Atten (dB)    P+V Corrn (dB), S.P.L. (dB)    THD (%)"
        resline ="%.1f        %.4f          %.4f          %.4f      %.2f          %.3f            %.2f           %.1f"
        
        def _print_instrument(header, resline, data, data_u):
            print(header)
            for row in data: 
                print(resline % (row['racal_dana'], row['Vmic'], row['Vins'], row['IV'], row['attenuation'],
                      data_u['pvcorr'], row['SPL'], row['thd']))
            mean_freq = sum(row['racal_dana'] for row in data) / len(data)
            mean_SPL = sum(row['SPL'] for row in data) / len(data)
            mean_thd = sum(row['thd'] for row in data) / len(data)
            # Racal Dana Freq + Uncertainty, Krohn Hite Freq = Uncertainty
            print("Mean Freq = %.2f Hz, Freq unc = %.2f Hz (k=2.00) Mean dist=%.2f%% Dist unc=%.2f%% (k=2.00)" %
                  (mean_freq, data_u['u_frequency'], mean_thd, data_u['u_thd']))
            print("Mean S.P.L. = %.2f" % mean_SPL)
            print("Type A unc = %.3f dB Total unc = %.3f dB" % (
                data_u['u_type_A'], data_u['u_total']))
            
        def _print_uncertainties(data_u):
            for key in data_u:
                print(key, data_u[key])
            
        print("Pressure %.2f Temperature %.2f Relative Humidity %.2f" % (
              env['pressure'], env['temperature'], env['relative_humidity']))
        print("Polarising Voltage %.2f" % env['polarising_voltage'])
        
        print("--- Working Standard Results ---")
        _print_instrument(header, resline, SPL_standard, standard_u)
        print("--- Customer Device Results ---")
        _print_instrument(header, resline, SPL_device, device_u)
        
        print("--- Working Standard Detailed Uncertainties ---")
        _print_uncertainties(standard_u)
        print("--- Customer Device Detailed Uncertainties ---")
        _print_uncertainties(device_u)