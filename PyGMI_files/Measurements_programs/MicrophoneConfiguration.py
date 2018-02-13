import logging
import pprint
import threading
import time

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
        self.keithley2001 = m.instr_1
        self.racaldana = m.instr_2
        self.agilent3350A = m.instr_3
        self.kh6880A = m.instr_4
        self.bk2636 = m.instr_5
        self.dpi141 = m.instr_6
        self.el100 = m.instr_7
                
        SPL_standard = []
        SPL_device = []
        env_conditions = []
                
        for i in range(5):           
            self.stop_switch_instrument("Reference Standard") 
            res = self.measure_SPL("Reference Standard")
            SPL_standard.append(res)
            
            self.stop_switch_instrument("Customer Device")
            res = self.measure_SPL("Customer Device") 
            SPL_device.append(res)               
        
        pprint.pprint(SPL_standard)
        pprint.pprint(SPL_device)                          
    
    def measure_SPL(self, device_name):
        """"Big process that is repeated 5 times for working standard
        and customer device. The final output is two arrays
        SPL_standard[5]
        SPL_device[5]
        """
        # initial env conditions         
        t1 = raw_input("Temperature?")
        rh1 = raw_input("Humidity?")
        p1 = 100.0  # TODO READ DPI141 
        vpol1 = None
       
        # check Keithley2001 DC & CURR stability/fluctuation. 
        dc_volt = self.keithley2001.scan_channel(5, "VOLT:DC", times=20, interval=0.99)
        self._check_stability(dc_volt)
        dc_curr = self.keithley2001.scan_channel(5, "VOLT:CURR", times=20, interval=0.99)
        self._check_stability(dc_curr)                
        
        # Read total harmonic distortion from Krohn Hite.
        kh_avg = self.kh6880A.read_average(times=10, delay=1.99)
        
        raw_input("Stop %s, press any key to continue..." % device_name)
        
        # start agilent3350A
        # the attenuator is adjusted until the voltage matches (to 0.005 db) the
        # output of the calibrator (VmicAmpl(ch5) - VinsertAmpl(ch5))           
        self.agilent3350A.turn_on()
        for val in range(90.00, 80.00, -0.5):
            attenuator_str = "%.2f" % val
            self.el100.set(attenuator_str)
            
        
        # measure Vins voltage (ch3) keythley
        dc_volt = self.keithley2001.scan_channel(3, "VOLT:DC", times=20, interval=0.99)
                
        rd_avg = self.racaldana.read_average(times=20, delay=1.99)
        # distortion value (kh6880A)
        kh_avg2 = self.kh6880A.read_average(times=10, delay=1.99)      
        
        # final env conditions 
        t2 = float(raw_input("Temperature?"))
        rh2 = float(raw_input("Humidity?"))
        p2 = float(self.dpi)
        vpol2 = None
        
        env = dict(t=(t1+t2)/2.0,
                   rh=(rh1+rh2)/2.0,
                   p=(p1+p2)/2.0,
                   vpol=(vpol1+vpol2)/2.0)
        
        return 0.0
    
    def stop_switch_instrument(self, device):
        print("Please connect and turn on the %s." % device)
        input("Please enter any key to continue when ready...")
    
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