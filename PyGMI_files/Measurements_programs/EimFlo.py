# -*- coding: utf-8 -*-

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
    def __init__(self,requestMessage, default_value=""):
        self.root = Tk()
        self.root.after(2000, lambda: self.e.focus_force())
        self.string = ''
        self.frame = Frame(self.root)
        self.frame.pack()        
        self.acceptInput(requestMessage, default_value)

    def acceptInput(self,requestMessage, default_value):
        r = self.frame
        k = Label(r,text=requestMessage)
        k.pack(side='left')
        self.e = Entry(r,text='Name')
        self.e.insert(END, default_value)
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

class TimerWindow(object):
    def __init__(self, resistance_callback=None, pressure_callback=None):
        self.t1 = 0.0
        self.t2 = 0.0
        self.duration = 0.0
        self.timer_running = False
        self.resistance_callback = resistance_callback
        self.pressure_callback = pressure_callback
        
        self.root = Tk()
        self.frame = Frame(self.root)
        self.frame.pack()
        self.acceptInput()
        
        self.resistance_measurements = []
        self.pressure_measurements = []
        
        
    def acceptInput(self):
        r = self.frame
        
        self.k = Label(r,text="TIMER")
        self.k.pack(side='left')
                
        self.label = Label(r, text="")
        self.label.pack()
        
        b1 = Button(r,text='Start',command=self.start)
        b1.pack(side='right')
        b1.focus_set()
        
        b2 = Button(r, text='Stop', command=self.stop)
        b2.pack(side='right')
        
    def start(self):
        self.t1 = datetime.utcnow()
        self.k.text = "Counter started"
        self.timer_running = True
        self.count_time()
        
    def stop(self):
        # disable count_time and calculate time
        self.count_time = lambda: True
        self.t2 = datetime.utcnow()
        self.timer_running = False
        self.duration = self.t2 - self.t1
        # close window
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()
        
    def count_time(self):
        """Record pressure and resistance values every 10''.
        """
        self.t2 = datetime.utcnow()
        self.duration = self.t2 - self.t1
        self.label.configure(text="%.4f" % self.duration.total_seconds())
        if self.timer_running:   
            self.frame.after(999, lambda: self.count_time())
        sec = round(self.duration.total_seconds())
        if sec == 0 or sec % 10 == 0:
            res = self.resistance_callback()
            self.resistance_measurements.append(res)
            pre = self.pressure_callback()
            self.pressure_measurements.append(pre)        
                    
    def waitForInput(self):
        self.root.mainloop()       

        
def getText(requestMessage, default_value=""):
    msgBox = takeInput(requestMessage, default_value=default_value)
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
        
        # STATIC variables that may change after equipment calibration.
        self.a = 0.00392
        self.b = -0.00000089049
        self.r = 99.98
        
    def run(self):
        """General configuration is loaded from C:\acoustics-configuration\general.yaml 
        """
        self.start_datetime = datetime.now()
                        
        logging.info("init all instruments")
        m=self.mainapp        
        self.mensor = m.instr_1   # GBIP0::16
        self.agilent3340 = m.instr_2      # GBIP0::14      
        
        t1 = float(getText("Current temperature (oC)").strip())
        rh1 = float(getText("Current humidity (%)").strip())
        pre = float(getText("Current pressure").strip())
        
        # Flows used in calibration are user-defined.
        flows_str = getText("Calibration flows (comma separated values)",
                            default_value="100,75,45,25,15").strip()
        flows = [int(fl.strip()) for fl in flows_str.split(",")]
        flow_unit = getText("Flow measurement unit (LPM, LPH, M3H)", default_value="LPM")
        results = []
        for flow in flows:
            wait("Flow = %d %s. Flow Adjustment in progress. Please press OK when ready." % (
                flow, flow_unit))
            vol = float(getText("Volume").strip())
            for iteration in [1,2,3]:
                while True:
                    line = self.measure(flow, flow_unit, vol, iteration, pre)
                    self._print_headers()
                    self._print_line(line)
                    confirm = getText("Deviation %.2f. Please type \"yes\" to continue or leave empty to repeat" % line['g_slpm_deviation'],
                                      default_value="yes")
                    if confirm == "yes":        
                        results.append(line)
                        break
                               
        self.end_datetime = datetime.now()        
        self.print_results(results, t1, rh1)
    
    def _convert_ohm_oc(self, val, pre):
        """Function from cell D46.
        """        
        nom = (-self.r * pre) + math.sqrt(self.r*pre)**2 - (4.0*self.r*self.b*(self.r-val))
        denom = (2.0*self.r*self.b)
        return nom / denom 
    
    def _convert_lpm_slpm(self, lpm, pre, res_oc):
        """Function from cell J46.
        """
        return lpm * (pre/1013.25) * (293.15/(res_oc + 273.15) )
    
    def measure(self, flow, flow_unit, vol, iteration, pre):
        wait("Flow %d %s Run %d/3" % (flow, flow_unit, iteration))        
             
        tw = TimerWindow(resistance_callback=self.agilent3340.read_resistance,
                         pressure_callback=self.mensor.read)
        tw.waitForInput()
        
        res_ohm = sum(tw.resistance_measurements) / len(tw.resistance_measurements)
        res_oc = self._convert_ohm_oc(res_ohm, pre)
        res_pre = sum(tw.pressure_measurements) / len(tw.pressure_measurements)
                
        t_sec = tw.duration.total_seconds()
        t_min = t_sec / 60.0
        g_lpm = vol / t_min 
        g_slpm = self._convert_lpm_slpm(g_lpm, pre, res_oc)
        g_slpm_real = float(getText("Real Flow Gm(SLPM);").strip())
        g_slpm_deviation = ((g_slpm - g_slpm_real) / g_slpm_real) * 100.0  
        
        return dict(flow=flow,
                    iteration=iteration,
                    res_ohm=res_ohm,
                    res_oc=res_oc,
                    pre=res_pre,
                    vol=vol,
                    t_sec=t_sec,
                    t_min=t_min,
                    g_lpm=g_lpm,
                    g_slpm=g_slpm,
                    g_slpm_real=g_slpm_real,
                    g_slpm_deviation=g_slpm_deviation
                    )
    
    def _print_headers(self):
        print("ΠΑΡΟΧΗ | ΑΡΙΘΜΟΣ | ΘΕΡΜ.ΕΞ | ΘΕΡΜ.ΕΞ | ΠΙΕΣΗ ΕΞ. |             ΕΝΔΕΙΞΗ ΟΡΓΑΝΟΥ             |   ΠΡΑΓΜΑΤΙΚΗ | ΑΠΟΚΛΙΣΗ")
        print("       | ΕΠΑΝΑΛ. |    Ω    |   oC    | mbar(abs) | V(L) | time | t(min) | G(LPM) | G(SLPM) | ΠΑΡ. Gm(SLPM)|    %")
    
    def _print_line(self, li):
        print("  %d   |    %d   |  %.2f  |  %.2f  |  %.2f  |  %d   | %.4f |  %.2f | %.2f | %.2f |  %.2f  |  %.2f" % (
            li['flow'], li['iteration'], li['res_ohm'], li['res_oc'], li['pre'],
            li['vol'], li['t_sec'], li['t_min'], li['g_lpm'], li['g_slpm'],
            li['g_slpm_real'], li['g_slpm_deviation']))
    
    def print_results(self, results, t_env, rh_env):  
        """This is copied by the user to produce the final certificate.
        """
        dif = self.end_datetime - self.start_datetime
        s = dif.total_seconds()
        dif_hours, remainder = divmod(s, 60)
        dif_min, dif_sec = divmod(remainder, 60)
        dif_str = "%02d:%02d:%02d" % (dif_hours, dif_min, dif_sec)
        print("Έναρξη %s Λήξη %s Διάρκεια %s" % (
            str(self.start_datetime).split(".")[0], str(self.end_datetime).split(".")[0], dif_str ))
        
        print("Περιβαλλοντικές Συνθήκες. Θερμοκρασία %.2f, Υγρασία %.2f" % (t_env, rh_env))
        self._print_headers()
        for li in results:
            self._print_line(li)