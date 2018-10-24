import logging 
import math
import numpy
import threading
import time
from Tkinter import *
import tkMessageBox
import winsound
import yaml
from datetime import datetime
from _hotshot import resolution


class takeInput(object):
    """Utility class to show popup and get user input string.
    """
    def __init__(self,requestMessage):
        self.root = Tk()
        self.root.after(2000, lambda: self.e.focus_force())
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
        self.e.bind('<Return>', self.gettext)
        b = Button(r,text='okay',command=self.gettext)
        b.pack(side='right')
        self.root.bind('<Return>', self.gettext)

    def gettext(self, event=None):
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
        """General configuration is loaded from C:\acoustics-configuration\general.yaml 
        """
        self.start_datetime = datetime.now()
        with open('C:/acoustics-configuration/general.yaml', 'r') as stream:
            self.GENERAL_CONF = yaml.load(stream)     
            assert self.GENERAL_CONF.get('ITERATIONS')
            assert self.GENERAL_CONF.get('WAIT_BEFORE_SPL_MEASUREMENT')
            assert self.GENERAL_CONF.get('FREQUENCY')
                
        # Must have c:/acoustics-configuration/<mic-type>.yaml or the program
        # will not continue
        mic_type = getText("Microphone type? (e.g. 4190)").strip()
        with open('C:/acoustics-configuration/microphones/%s.yaml' % mic_type, 'r') as stream:
            self.MIC_CONF = yaml.load(stream)
            
        calibrator_type = getText("Reference Calibrator type? (e.g. XXX)").strip()
        with open('C:/acoustics-configuration/calibrators/%s.yaml' % calibrator_type, 'r') as stream:
            self.REF_CALIBRATOR_CONF = yaml.load(stream)
            
        calibrator_type = getText("Customer Calibrator type? (e.g. XXX)").strip()
        with open('C:/acoustics-configuration/calibrators/%s.yaml' % calibrator_type, 'r') as stream:
            self.CUSTOMER_CALIBRATOR_CONF = yaml.load(stream)
            
        #        Kpv
        #        ??
        # TODO which settings go in there?
        self.calibrator_nominalevel = int(getText("Calibrator Nominal Level (94, 104 or 114dB)").strip())
        self.mic_type = mic_type
        self.micsensitivity = float(self.MIC_CONF.get("SENSITIVITY"))
        self.mic_serial_number = self.MIC_CONF.get("SERIAL_NUMBER")
        
        # DEBUGGING
        # self.debug_print()
        # sys.exit(0)
        
        logging.info("init all instruments")
        m=self.mainapp        
        self.keithley2001 = m.instr_1   # GBIP0::16
        self.racaldana = m.instr_2      # GBIP0::14
        self.waveform_generator = m.instr_3   # GBIP0::20
        self.kh6880A = m.instr_4        # GBIP0::1
        self.bk2636 = m.instr_5         # GBIP0::4
        self.dpi141 = m.instr_6         # GBIP0::2
        self.el100 = m.instr_7          # GBIP0::3                                 
        self.el100.set("99.99")
        self.waveform_generator.turn_off()
        
        t1 = float(getText("Initial temperature (oC)").strip())
        rh1 = float(getText("Initial humidity (%)").strip())
        p1 = self.dpi141.read() 
        vpol1 = self.keithley2001.scan_channel(4, "VOLT:DC")[0]
        self.check_temperature(t1)
        self.check_humidity(rh1)
        self.check_pressure(p1)
        self.check_vpol(vpol1)
        
        self.bk2636.decide_set_gain(self.calibrator_nominalevel, self.micsensitivity)
        SPL_standard = []
        SPL_device = []
        wait_time = self.GENERAL_CONF.get('WAIT_BEFORE_SPL_MEASUREMENT')
        for cnt in range(self.GENERAL_CONF.get('ITERATIONS')):           
            self.stop_switch_instrument("Reference Standard")
            # delay time necessary for calibrator
            print("Wait for %d sec" % wait_time)
            time.sleep(wait_time)
            res1 = self.measure_SPL("Reference Standard", v_pol=vpol1)
            print("Step %d of %d" % (cnt+1, self.GENERAL_CONF.get('ITERATIONS')))
            self.print_current_result(res1)
            SPL_standard.append(res1)
            
            self.stop_switch_instrument("Customer Device")
            print("Wait for %d sec" % wait_time)
            time.sleep(wait_time)
            res2 = self.measure_SPL("Customer Device", v_pol=vpol1)
            print("Step %d of %d" % (cnt+1, self.GENERAL_CONF.get('ITERATIONS')))
            self.print_current_result(res2) 
            SPL_device.append(res2)               
        
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
        self.end_datetime = datetime.now()        
        self.print_results(env, SPL_standard, SPL_device, standard_uncertainty,
                           device_uncertainty)               
    
    def measure_SPL(self, device_name, v_pol):
        """"Big process that is repeated 5 times for working standard
        and customer device. The final output is a dict with all measurements.
        """               
        self.waveform_generator.turn_off()
       
        # Read Total Harmonic Distortion (THD) from Krohn Hite.
        kh_list1 = self.kh6880A.read(times=10, delay=0.99)

        kh_avg1 = sum(kh_list1) / len(kh_list1)
        print("AVG DISTORTION", kh_list1)
    
        # check Keithley2001 DC & CURR stability/fluctuation. MA o/p (V) is vmic 
        dc_volt = self.keithley2001.scan_channel(5, "VOLT:DC", times=15, interval=0.99)
        spl_fluctuation = self.check_fluctuation(dc_volt)
        vmic = round(sum(dc_volt) / len(dc_volt), 5)
        print("RACAL1")
        rd_values = self.racaldana.read_list(times=10, delay=0.90)  # very slow to respond
        rd_avg = round(sum(rd_values) / len(rd_values), 3)
        # Check that Racal Dana frequency is +/-10% of waveform generator frequency
        frequency = float(self.GENERAL_CONF.get('FREQUENCY'))
        freq_up = 1.1 * frequency
        freq_down = 0.9 * frequency
        freq_fluctuation = self.check_fluctuation(rd_values)        
        logging.info("Racal Dana average read %g, allowed range: [%g, %g].",
                     rd_avg, freq_down, freq_up)
        if rd_avg < freq_down or rd_avg > freq_up:
            wait("Critical Error! Racal Dana value %g outside range: [%g, %g]. Terminating program." % (
                rd_avg, freq_down, freq_up))
            sys.exit(0)
        
        wait("Stop %s, press any key to continue..." % device_name)
        if device_name == "Customer Device":
            wait("Please connect the Reference Standard and press any key to continue...")
                
        # start agilent3350A, send 6V peak to peak, freq 1000Hz, SINE waveform.
        # the attenuator is adjusted until the voltage matches (to 0.005 db) the
        # output of the calibrator (VmicAmpl(ch5) - VinsertAmpl(ch5))           
        # Vdev = Vmic
        # Vsys = Vins
        # atten#=100.0# - micsensitivity# - nomlevel#
        # micsensivity input variable by user (certificate). e.g. value = -26.49
        # calibrator nominal level e.g. value = 94
        self.waveform_generator.turn_on()
        frequency = int(self.GENERAL_CONF.get('FREQUENCY'))
        self.waveform_generator.set_frequency(frequency, 6.0)
        atten = 100.0 - self.micsensitivity - self.calibrator_nominalevel
        good_consec = 0
        vins = 0.0
        while good_consec < 2:
            attenuator_str = "%05.2f" % atten
            self.el100.set(attenuator_str)
            time.sleep(1)
            vins_list = self.keithley2001.scan_channel(5, "VOLT:DC", times=5, interval=0.99)
            vins = round(sum(vins_list)/len(vins_list), 3)
            print("atten keithley channel 5 DC", vins, "vmic", vmic)
            # MA o/p (V) is vins         
            # convert to dB and check value < 0.005 two times for success
            attenerror = round(20.0 * math.log10(vmic / vins), 3)
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
                
        thd = sum(kh_list1) / len(kh_list1)        
        SPL = self.uncorrected_sound_pressure_level(vins_source3, atten,
                                                    self.micsensitivity)        
        # SPL correction for polarisation voltage
        SPL -= math.log10(v_pol / 200.0)
        # TODO SPL correction for pressure        
        self.waveform_generator.turn_off()
        return dict(attenuation=atten,
                    thd=thd,
                    krohn_hite=kh_avg1,
                    racal_dana=rd_avg,
                    SPL=SPL,
                    Vmic=vmic,      # MA_op first
                    Vins=vins,      # MA_op second
                    IV=vins_source3,
                    spl_fluctuation=spl_fluctuation,
                    freq_fluctuation=freq_fluctuation)    
        
    def uncorrected_sound_pressure_level(self, Vins, A, M):
        """SPL calculation. Params:
        Vins: measured insert voltage
        A: attenuation (dB)
        M: sensitivity (dB re 1 VPa-1)
        Output: SPL
        """
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
            logging.error("Program exit")
            sys.exit(0)
            
    def check_fluctuation(self, v_list):
        """Calculate fluctuation for a list of values.
        V channel 5 fluctuation
        If over a limit, stop program
        If under a limit, show class
        Show fluctuation in the results.
        """
        mean_val = sum(v_list) / len(v_list)
        max_val = max(v_list)
        min_val = min(v_list)
        highest_fluctuation = 20 * math.log10(max_val / mean_val)
        lowest_fluctuation = 20 * math.log10(min_val/ mean_val)
        check = max(abs(highest_fluctuation), abs(lowest_fluctuation))
        if check > 0.3:   
            print(v_list)
            logging.error("Fatal problem with measurement fluctuation %g", check)
            sys.exit(0)
        return check
    
    def calculate_uncertainties(self, measurements, env):
        IVu = self.voltmeter_uncertainty(1.0005)    # value from certificate
        IVe = self.voltmeter_uncertainty(1.0003)    # value from certificate
        
        avg_attenuation = sum([row['attenuation'] for row in measurements]) / len(measurements)
        Au = self.attenuator_uncertainty(avg_attenuation)
        Ae = self.attenuator_error(avg_attenuation)
        
        Mu = self.MIC_CONF.get('SENSITIVITY_UNCERTAINTY')   # value from certificate
        Mp = 0.038   # table page 24 of 42     TODO table logic in function to decide Mp
        Mt = 0.05    # table page 25 of 42      TODO table logic in function to decide Mt
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
        spl_repeatability = max(numpy.std(spls), 0.0045) 
        spl_repeatability2 = pow(spl_repeatability, 2)
                
        total = u_IVu2 + u_IVe2 + u_Au2 + u_Ae2 + u_Mu2 + u_Mp2 + u_Mt2 + u_MM2 + u_Kpv2 +\
                u_Kp2 + u_Kmv2 + u_SPLr2 + spl_repeatability2
        total = math.sqrt(total)
        pcorr = 0.0 # TODO Pressure correction. YIANIS 
        vcorr = -20.0 * math.log10(env['polarising_voltage'] / 200.0)
        pvcorr = round(pcorr + vcorr, 3)
        distortions = numpy.array([item['krohn_hite'] for item in measurements])
        frequencies = numpy.array([item['racal_dana'] for item in measurements])
        self.check_fluctuation(frequencies)
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
            SPLr=u_SPLr,
            spl_repeatability=spl_repeatability,
            total=total, 
            u_total=total * 2.0,
            u_thd=self.distortion_analyser_uncertainty(distortions) * 2.0,
            u_SPL=spl_repeatability2 * 2.0,
            u_typeA=spl_repeatability2 * 2.0,
            u_frequency=self.frequency_uncertainty(frequencies) * 2.0,
            pvcorr=pvcorr
            )
     
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
        return dict(IVu=u_IVu,
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
                    total=round(math.sqrt(total), 3))
    
    def frequency_uncertainty(self, frequencies):
        """"Calibration of Sound Calibrators Method, 17.6 Typical uncertainty budget
        """
        sqrt3 = math.sqrt(3)
        Frequency_counter_u = math.pow(0.01 / 2.0, 2)
        Frequency_counter_error  = math.pow(0.01 / sqrt3, 2)
        Resolution = math.pow(0.05 / sqrt3, 2)
        Repeatability = math.pow(max(numpy.std(frequencies) * 2.0, 0.0224), 2)
        combined = Frequency_counter_u + Frequency_counter_error + Resolution + Repeatability
        return round(math.sqrt(combined), 4)
    
    def distortion_analyser_uncertainty(self, distortions):
        sqrt3 = math.sqrt(3)
        Distortion_analyser_u = math.pow(0.05 / 2.0, 2)
        Distortion_analyser_error = math.pow(0.2 / sqrt3, 2)
        Resolution = math.pow(0.05 / sqrt3, 2)
        Repeatability = math.pow(max(numpy.std(distortions) * 2.0, 0.0447), 2)
        combined = Distortion_analyser_u + Distortion_analyser_error + Resolution + Repeatability
        return round(math.sqrt(combined), 4)
    
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
    
    
    def print_current_result(self, row):
        header = "Freq      Freq Fluc    MA o/p    MA o/p    IV    Atten    P+V Corrn       S.P.L.   S.P.L. Fluc    THD\n" +\
                 "(Hz)         (Hz)       (V)       (V)     (V)    (dB)        (dB)          (dB)      (dB)         (%)"
        resline = "%.1f    %.4f     %.4f     %.4f     %.2f   %.3f     %.2f       %.2f        %.2f       %.1f"
        print(header)
        print(resline % (row['racal_dana'], row['freq_fluctuation'], row['Vmic'], row['Vins'], row['IV'], row['attenuation'],
                         0.0, row['SPL'], row['spl_fluctuation'], row['thd']))
    
    def print_results(self, env, SPL_standard, SPL_device, standard_u, device_u):  
        """This is copied by the user to produce the final certificate.
        """
        header = "Freq      Freq Fluc    MA o/p    MA o/p    IV    Atten    P+V Corrn       S.P.L.   S.P.L. Fluc    THD\n" +\
                 "(Hz)         (Hz)       (V)       (V)     (V)    (dB)        (dB)          (dB)      (dB)         (%)"
        resline = "%.1f    %.4f     %.4f     %.4f     %.2f   %.3f     %.2f       %.2f        %.2f       %.1f"
        
        def _print_instrument(header, resline, data, data_u):
            print(header)
            for row in data: 
                print(resline % (row['racal_dana'], row['freq_fluctuation'], row['Vmic'], row['Vins'], row['IV'], row['attenuation'],
                      data_u['pvcorr'], row['SPL'], row['spl_fluctuation'], row['thd']))

            mean_freq = sum(row['racal_dana'] for row in data) / len(data)
            mean_SPL = sum(row['SPL'] for row in data) / len(data)
            mean_thd = sum(row['thd'] for row in data) / len(data)
            # Racal Dana Freq + Uncertainty, Krohn Hite Freq = Uncertainty
            print("Mean Freq = %.2f Hz, Freq unc = %.1f Hz (k=2.00) Mean dist=%.2f%% Dist unc=%.1f%% (k=2.00)" %
                  (mean_freq, data_u['u_frequency'], mean_thd, data_u['u_thd']))
            print("Mean S.P.L. = %.2f, Type A unc = %.3f dB Total unc = %.2f dB" % 
                  (mean_SPL, data_u['u_typeA'], data_u['u_total']))
                        
        def _print_uncertainties(data_u):
            out = ""
            for (i, key) in enumerate(data_u):
                out += "%s\t%.4f\t" % (key, data_u[key])
                if (i+1) % 5 == 0:
                    out += "\n"
            print(out)
            
        print("Microphone Type: %s Serial Number: %s sensitivity %.3f (dB)" % (
            self.mic_type, self.mic_serial_number, self.micsensitivity))
        ref_cal = self.REF_CALIBRATOR_CONF
        print("Reference Calibrator Type: %s Manufacturer: %s Serial Number: %s" % (
            ref_cal.get('type'), ref_cal.get('manufacturer'), ref_cal.get('serial_number')
            ))
        customer_cal = self.CUSTOMER_CALIBRATOR_CONF
        print("Customer Calibrator Type: %s Manufacturer: %s Serial Number: %s" % (
            customer_cal.get('type'), customer_cal.get('manufacturer'), customer_cal.get('serial_number')))
        print("Customer Company: %s" % customer_cal.get('company'))
        
        dif = self.end_datetime - self.start_datetime
        s = dif.total_seconds()
        dif_hours, remainder = divmod(s, 60)
        dif_min, dif_sec = divmod(remainder, 60)
        dif_str = "%02d:%02d:%02d" % (dif_hours, dif_min, dif_sec)
        print("Calibration start %s end %s duration %s" % (
            str(self.start_datetime).split(".")[0], str(self.end_datetime).split(".")[0], dif_str ))
        
        print("Pressure %.2f, Temperature %.2f, Relative Humidity %.2f, Polarising Voltage %.2f" % (
              env['pressure'], env['temperature'], env['relative_humidity'], env['polarising_voltage']))
        
        print("--- Working Standard Results ---")
        _print_instrument(header, resline, SPL_standard, standard_u)
        print("--- Customer Device Results ---")
        _print_instrument(header, resline, SPL_device, device_u)
        
        print("--- Working Standard Detailed Uncertainties ---")
        _print_uncertainties(standard_u)
        print("--- Customer Device Detailed Uncertainties ---")
        _print_uncertainties(device_u)
        
    def debugging_script(self):
        """debugging script to run to check things. NOT used normally.
        agilent on, kh on, racal on
        keithley 2001 must read channel 3 AC, value 1 V
        """      
        self.waveform_generator.turn_on()
        v_test = self.keithley2001.scan_channel(3, "VOLT:AC")
        print(v_test)    
        sys.exit(0)
        
        """"
        
    def debug_print(self):
        #Use 0 values everywhere, try to debug the final report printout.
        
        self.end_datetime = datetime.now()
        env = dict(temperature=10.0, relative_humidity=10.0,
                   pressure=1000.0, polarising_voltage=100.0)
        
        row = dict(attenuation=10.0,
                    thd=0.0,
                    krohn_hite=0.0,
                    racal_dana=0.0,
                    SPL=0.0,
                    Vmic=0.0,
                    Vins=0.0,
                    IV=0.0,
                    spl_fluctuation=0.0,
                    freq_fluctuation=0.0)
        SPL_standard = SPL_device = [row, row, row, row, row]
        standard_uncertainty = dict(IVu=0.0,
                                    IVe=0.0,
                                    Au=0.0,
                                    Ae=0.0,
                                    Mu=0.0,
                                    Mp=0.0,
                                    Mt=0.0,
                                    MM=0.0,
                                    Kpv=0.0,
                                    Kp=0.0,
                                    SPLr=0.0,
                                    spl_repeatability=0.0,
                                    total=0.0, 
                                    u_total=0.0,
                                    u_thd=0.0,
                                    u_SPL=0.0,
                                    u_typeA=0.0,
                                    u_frequency=0.0,
                                    pvcorr=0.0)
        device_uncertainty = standard_uncertainty
        self.print_results(env, SPL_standard, SPL_device, standard_uncertainty,
                           device_uncertainty)
        """