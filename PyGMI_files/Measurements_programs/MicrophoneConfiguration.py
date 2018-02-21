import logging
import pprint
import threading
import time
from Tkinter import *
import tkMessageBox

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
        # TODO PROBLEM HERE  
        #print("before")      
        #t1 = 19 # getText("Current temperature?") # TODO input("Temperature?")
        #print(t1)
        #print("-----------------")
        t1 = 20
        rh1 = 50.0 # TODO input("Humidity?")
        p1 = 100.0  # TODO READ DPI141 
        vpol1 = None
       
        # check Keithley2001 DC & CURR stability/fluctuation. 
        dc_volt = self.keithley2001.scan_channel(5, "VOLT:DC", times=20, interval=0.99)
        self._check_stability(dc_volt)
        dc_curr = self.keithley2001.scan_channel(5, "VOLT:CURR", times=20, interval=0.99)
        self._check_stability(dc_curr)                
        
        # Read total harmonic distortion from Krohn Hite.
        kh_avg = self.kh6880A.read_average(times=10, delay=1.99)
        logging.info("Kron Hite 6880A read %g", kh_avg)
        print("Stop %s, press any key to continue..." % device_name)
        wait()
        
        # start agilent3350A
        # the attenuator is adjusted until the voltage matches (to 0.005 db) the
        # output of the calibrator (VmicAmpl(ch5) - VinsertAmpl(ch5))           
        self.agilent3350A.turn_on()
        #for val in range(90.00, 80.00, -0.5):
        #    attenuator_str = "%.2f" % val
        #    self.el100.set(attenuator_str)
        
        # measure Vins voltage (ch3) keythley
        dc_volt = self.keithley2001.scan_channel(3, "VOLT:DC", times=20, interval=0.99)
        print(dc_volt)
        #logging.info("Keithley DC VOLT %g", dc_volt)
        rd_avg = self.racaldana.read_average(times=20, delay=1.99)
        logging.info("Racal Dana read %g", rd_avg)
        # distortion value (kh6880A)
        kh_avg2 = self.kh6880A.read_average(times=10, delay=1.99)      
        logging.info("Kron Hite 2 read average %g", kh_avg2)
        
        # final env conditions 
        t2 = 20.5     # float(input("Temperature?"))
        rh2 = 45.0    # float(input("Humidity?"))
        p2 = float(self.dpi)
        vpol2 = None
        
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