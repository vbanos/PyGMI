import logging
import math
import pprint
import threading
import time
from Tkinter import *
import tkMessageBox

#from microphone_uncertainties import attenuator_uncertainty


class takeInput(object):

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
        self.root.destroy()

    def getString(self):
        return self.string

    def waitForInput(self):
        self.root.mainloop()

def getText(requestMessage):
    msgBox = takeInput(requestMessage)
    #loop until the user makes a decision and the window is destroyed
    msgBox.waitForInput()
    msg = msgBox.getString()
    msgBox.root.quit()
    msgBox.root.destroy()
    return msg

def wait(msg):
    """Wait until any key is pressed.
    """
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
        
        logging.info("init all instruments")
        self.keithley2001 = m.instr_1   # GBIP0::16
        self.racaldana = m.instr_2      # GBIP0::14
        self.agilent3350A = m.instr_3   # GBIP0::20
        self.kh6880A = m.instr_4        # GBIP0::1
        self.bk2636 = m.instr_5         # GBIP0::4
        self.dpi141 = m.instr_6         # GBIP0::2
        self.el100 = m.instr_7          # GBIP0::3
                
        SPL_standard = []
        SPL_device = []
        env_conditions = []
        
        # TODO PROBLEM with gain setting in BK2636
        # gain setting configured by mic sensitivity
        # line 1235 in BAS file.
        # TODO input gain + output gain        
        for i in range(5):           
            self.stop_switch_instrument("Reference Standard") 
            res = self.measure_SPL("Reference Standard")
            SPL_standard.append(res)
            self.stop_switch_instrument("Customer Device")
            res = self.measure_SPL("Customer Device") 
            SPL_device.append(res)
            # TODO remove this 
            break               
        
        pprint.pprint(SPL_standard)
        pprint.pprint(SPL_device)
        
        #self.calculate_uncertainties(SPL_standard, SPL_device, env_conditions)
    
    def measure_SPL(self, device_name):
        """"Big process that is repeated 5 times for working standard
        and customer device. The final output is two arrays
        SPL_standard[5]
        SPL_device[5]
        """
        # initial env conditions
        # TODO PROBLEM HERE  
        #print("before")      
        #t1 = 19 # getText("Current temperature?") # TODO input("Temperature?")
        #print(t1)
        #print("-----------------")
        
        self.agilent3350A.turn_off()
        
        t1 = 20
        rh1 = 50.0 # TODO input("Humidity?")
        p1 = self.dpi141.read() 
        vpol1 = self.keithley2001.scan_channel(4, "VOLT:DC")[0]
        
        self.check_temperature(t1)
        self.check_humidity(rh1)
        self.check_pressure(p1)
        self.check_vpol(vpol1)
       
        # check Keithley2001 DC & CURR stability/fluctuation. 
        dc_volt = self.keithley2001.scan_channel(5, "VOLT:DC", times=20, interval=0.99)
        self._check_stability(dc_volt)
        
        vmic = sum(dc_volt) / len(dc_volt)
        
        # Read total harmonic distortion from Krohn Hite.
        kh_avg = self.kh6880A.read_average(times=10, delay=1.99)
        logging.info("Kron Hite 6880A read %g", kh_avg)
        wait("Stop %s, press any key to continue..." % device_name)
        
        
        # start agilent3350A
        # the attenuator is adjusted until the voltage matches (to 0.005 db) the
        # output of the calibrator (VmicAmpl(ch5) - VinsertAmpl(ch5))           
        self.agilent3350A.turn_on()
        # FIRST agilent gives 6V peak to peak, freq 1000Hz, SINE waveform
        
        # Vdev = Vmic
        # Vsys = Vins
        
        # atten#=100.0# - micsensitivity# - nomlevel#
        # micsensivity input variable by user (certificate). e.g. value -26.49
        # nomlevel = 94
        # 100 - (-26.49) - 94 = 32.49
        atten = 100.0 - (-26.49) - 94
        good_consec = 0 
        while good_consec < 2:
            print(atten)
            attenuator_str = "%.2f" % atten
            self.el100.set(attenuator_str)
            vins = self.keithley2001.scan_channel(5, "VOLT:DC")[0]
            print("vmic", vmic)
            print("vins", vins)         
            print("------------------------")   
            # convert to dB
            attenerror = abs(20.0 * math.log10(vmic / vins))
            if attenerror <= 0.005:
                good_consec += 1
                print("SUCCESS", attenerror)
            else:
                print("ERROR", attenerror)
                atten -= attenerror
                time.sleep(5)
        
        # measure Vins voltage (ch3) keythley
        dc_volt = self.keithley2001.scan_channel(3, "VOLT:DC", times=20, interval=0.99)
        print(dc_volt)
        #logging.info("Keithley DC VOLT %g", dc_volt)
        rd_avg = self.racaldana.read_average(times=20, delay=1.99)
        # rd_avg = 1
        logging.info("Racal Dana read %g", rd_avg)
        # distortion value (kh6880A)
        kh_avg2 = self.kh6880A.read_average(times=10, delay=1.99)      
        logging.info("Kron Hite 2 read average %g", kh_avg2)
        
        # final env conditions 
        t2 = 20.5     # float(input("Temperature?"))
        rh2 = 45.0    # float(input("Humidity?"))
        p2 = self.dpi141.read()
        vpol2 = self.keithley2001.scan_channel(4, "VOLT:DC")[0]
        
        self.check_temperature(t2)
        self.check_humidity(rh2)
        self.check_pressure(p2)
        self.check_vpol(vpol2)
        
        env = dict(t=(t1+t2)/2.0,
                   rh=(rh1+rh2)/2.0,
                   p=(p1+p2)/2.0,
                   vpol=(vpol1+vpol2)/2.0)
        logging.info(env)
        return 0.0
    
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
            msg = "Humidity %g outside preferred range of 50+-20%." % rh
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
        
    def calculate_uncertainties(self, SPL_standard, SPL_device, env_conditions):
        print("TODO")