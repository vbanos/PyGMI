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
                        
        logging.info("init all instruments")
        m=self.mainapp        
        self.mensor = m.instr_1   # GBIP0::16
        self.agilent3340 = m.instr_2      # GBIP0::14
        
        t1 = float(getText("Current temperature (oC)").strip())
        rh1 = float(getText("Current humidity (%)").strip())
        
        results = []
        for flow in [100]:  # , 75, 45, 25, 15]:
            for iteration in [1,2,3]:
                res = self.measure(flow, iteration)
                results.append(res)
                               
        self.end_datetime = datetime.now()        
        self.print_results(results, t1, rh1)
    
    def measure(self, flow, iteration):
        wait("ΠΑΡΟΧΗ %d ΕΠΑΝΑΛΗΨΗ %d" % (flow, iteration))
        
        res_ohm = self.agilent3340.read_resistance()
        res_oc = res_ohm + 1 # TODO conversion
        
        return dict(flow=flow,
                    iteration=iteration,
                    res_ohm=res_ohm,
                    res_oc=res_oc,
                    pre=self.mensor.read())
    
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
        print("ΠΑΡΟΧΗ | ΑΡΙΘΜΟΣ | ΘΕΡΜ.ΕΞ | ΘΕΡΜ.ΕΞ | ΠΙΕΣΗ ΕΞ. | ΕΝΔΕΙΞΗ ΟΡΓΑΝΟΥ")
        print("       | ΕΠΑΝΑΛ. |    Ω    |   oC    | mbar(abs) |                ")
        for li in results:
            print("  %d   |    %d   |  %.2f  |  %.2f  |  %.2f  | " % (
                li['flow'], li['iteration'], li['res_ohm'], li['res_oc'], li['pre']))