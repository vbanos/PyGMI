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
        
        self.keithley2001 = m.instr_1
        self.agilent3350A = m.instr_2
        self.bk2636 = m.instr_3
        self.kh6880A = m.instr_4
        self.racaldana = m.instr_5
        self.dpi141 = m.instr_6
    
        # HOW TO INITIALIZE ALL instruments, set parameters? TODO    

        self._keithley_wait_until_dc_voltage(0.5)
        
        # keithley read dc voltage 20 times, 1 sec interval ???
        # start triggering keithley2001
        #
        # i..ret% = kei2001.conf.trig.meas (kei2001%, 6%, 0%, 20&, 1%, 2%, 0.0#, 1.0#)
        # rem set up DMM buffer to store measurements, using auto buffer sizing, and start triggering
        # i..ret% = kei2001.conf.buf (kei2001%, 0%, 0%, 1%, 100&, 1%, 0%, 3%)
        #           
        # read 20 DC voltage from Keithley2001 with 1 sec interval 
        dc_v = []
        for _ in range(20):
            dc_v.append(self.keithley2001.query_voltage_average())
            time.sleep(1)
       
        self._check_stability(dc_v)
    
        # CHECK stability of measurements
        """
        rem get voltage readings
        i..ret% = kei2001.retrieve.meas (kei2001%, 20%, stabvoltage#())
        rem if last voltage<<first then message and flag
        IF (stabvoltage#(19%)/stabvoltage#(0%))<0.7 THEN
          mess%=fmt(message1$,"%s<%s","Faulty reading: device finished too early?")
          mess%=fmt(message2$,"%s<%s","Restart and click on Continue.")
          CALL mesconstop(message1$,message2$)
          flag%=1
        ENDIF
        CALL StdDev(stabvoltage#(),20%,meanvoltage#,sdvolt#)
        END SUB
        
        # if frequency stability is bad, stop error with calibrator !!!
        # if voltage stability is bad, stop error with calibrator !!!
        """        
        # racal dana average of 20 values
        rd_value = self.racal_dana_read()
        
        # keithley check voltage in channel 5 SUB wait.for.calibrator.to.stop(meanvoltage#)
        kh_value = self._kron_hite_read()
               
        """
        #data_queue=self.data_queue  #a shortcut to a FIFO queue to send the data to the main thread
        #######################################################
        #SAVEFILE HEADER - add column names to this list in the same order
        #as you will send the results of the measurements to the main thread
        #for example if header = ["Time (s)","I (A)","V (volt)"]
        #then you have to send the results of the measurements this way :
        #"self.data_queue.put(([some time, some current, some voltage],False))"
        header=['Time (s)']
        header+=['Time (min)']
        if f.temp_controller_on:header+=["T (K)"]
        if f.instr_on_1:header+=["Radius (V)","theta"]
        
        #######################################################
        #ORIGIN OF TIME FOR THE EXPERIMENT
        start_time=time.clock()
        #######################################################
        #SEND THE HEADER OF THE SAVEFILE BACK TO THE MAIN THREAD, WHICH WILL TAKE CARE OF THE REST
        self.data_queue.put((header,True))

        if f.instr_on_1:m.instr_1.set_amplitude(f.voltage1)
        
        #######Control parameters loop(s)######
        while True:
            #Check if the main thread has raised the "Stop Flag"
            if self.stop_flag.isSet():
                break
            #reserve the access to the instruments, then discuss with them
            with reserved_bus_access:
                #Measure T
                if f.temp_controller_on:T=m.temp_controller.query_temp('B')
                #Measure R and theta
                if f.instr_on_1:freq,R1,theta1=m.instr_1.query_f_R_theta()
                #Measure R and theta
                if f.instr_on_1:freq,R2,theta2=m.instr_1.query_f_R_theta()
            R=(R1+R2)/2.0
            theta=(theta1+theta2)/2.0
            ######Compile the latest data######
            t=time.clock()-start_time
            last_data=[t,t/60.0]
            if f.temp_controller_on:last_data.append(T)
            if f.instr_on_1:last_data.extend([R,theta])
                            
            #######Send the latest data to the main thread for automatic display and storage into the savefile######
            self.data_queue.put((last_data,False))
            
            #Check if the main thread has raised the "Stop Flag"
            if self.stop_flag.isSet():
                break            
            #######Wait mesure_delay secs before taking next measurements
            time.sleep(f.mesure_delay)
        """
    
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
    
    def _racal_dana_read(self):
        """Read 10 freq in 2sec intervals from Racal Dana. Return mean value.
        """
        results = []
        for _ in range(10):
            results.append(self.racaldana.read())
            time.sleep(1.99)
        return float(sum(results) / len(results))
    
    def _krohn_hite_read(self):
        """Read total harmonic distortion from Krohn Hite.
        """
        results = []
        for _ in range(10):
            results.append(self.kh6880A.read())
            time.sleep(1.99) 
        return float(sum(results) / len(results))
    
    def _check_stability(self, values):
        """Input is list of floats. If last/first value < 0.7, faulty reading.
        Exit with an error"""
        if values[-1] / values[0] < 0.7:
            logging.error("Fatal problem with measurement stability.")
            logging.error(values)
            sys.exit(0)