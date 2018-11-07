from Tkinter import *
import tkMessageBox
import winsound

class selectMethods60651(object):
    """Display ISO60651 methods and select which ones to execute (BS7580).
    """
    def __init__(self):
        self.root = Toplevel()
        self.acoustic_test = BooleanVar()
        chk = Checkbutton(self.root, text="Acoustic Test",
                          variable=self.acoustic_test)
        chk.pack()
        self.self_generated_noise_test = BooleanVar()
        chk0 = Checkbutton(self.root, text="Self-generated Noise Test (5.5.2 BS7580, Part 1)",
                           variable=self.self_generated_noise_test)
        chk0.pack()
        self.frequency_weighting = BooleanVar()
        chk1 = Checkbutton(self.root, text="Frequency Weighting (Subclause 5.5.4 of BS7580: Part 1).",
                           variable=self.frequency_weighting)
        chk1.pack()
        self.linearity = BooleanVar()
        chk2 = Checkbutton(self.root, text="Linearity (Subclause 5.5.3 of BS 7580: Part 1).",
                           variable=self.linearity)
        chk2.pack()
        self.time_weighting = BooleanVar()
        chk3 = Checkbutton(self.root, text="Time Weighting (Subclause 5.5.5 and 5.5.8 of BS 7580: Part 1).",
                           variable=self.time_weighting)
        chk3.pack()
        self.rms_accuracy_and_overload = BooleanVar()
        chk4 = Checkbutton(self.root, text="RMS Accuracy and Overload (Subclauses 5.5.7 and 5.5.12 of BS 7580: Part 1).",
                           variable=self.rms_accuracy_and_overload)
        chk4.pack()
        self.peak_response = BooleanVar()
        chk5 = Checkbutton(self.root, text="Peak Response (Subclauses 5.5.6 of BS 7580: Part 1).",
                           variable=self.peak_response)
        chk5.pack()
        self.time_averaging = BooleanVar()
        chk6 = Checkbutton(self.root, text="Time Averaging (Subclauses 5.5.9 of BS 7580: Part 1).",
                           variable=self.time_averaging)
        chk6.pack()
        self.pulse_range_sound_exposure_level_and_overload = BooleanVar()
        chk7 = Checkbutton(self.root, text="Pulse Range Sound Exposure Level & Overload (Subclauses 5.5.10, 5.5.11 and 5.5.12 of BS 7580: Part 1).",
                           variable=self.time_averaging)
        chk7.pack()
                
        b = Button(self.root,text='OK',command=self.get_selection)
        b.pack(side='bottom')

    def waitForInput(self):
        self.root.mainloop()
        
    def get_selection(self):
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()


class selectMethods616723(object):
    """Display ISO61672-3 methods and select which ones to execute.
    """
    def __init__(self):
        self.root = Toplevel()
        self.acoustic_test = BooleanVar()
        chk = Checkbutton(self.root, text="Acoustic Test",
                          variable=self.acoustic_test)
        chk.pack()
        self.self_generated_noise_test = BooleanVar()
        chk0 = Checkbutton(self.root, text="Self-generated Noise Test (5.5.2 BS7580, Part 1)",
                           variable=self.self_generated_noise_test)
        chk0.pack()
        self.frequency_weighting = BooleanVar()
        chk1 = Checkbutton(self.root, text="Frequency Weighting (61672-3 Electrical Tests, Par.12)",
                           variable=self.frequency_weighting)
        chk1.pack()
        self.freq_time_weighting = BooleanVar()
        chk2 = Checkbutton(self.root, text="Frequency and Time Weighting (61672-3 Electrical Tests, Par.13)",
                           variable=self.freq_time_weighting)
        chk2.pack()
        self.linearity = BooleanVar()
        chk3 = Checkbutton(self.root, text="Linearity (61672-3 Electrical Tests Par.14, 15)",
                           variable=self.linearity)
        chk3.pack()       
        self.toneburst_response = BooleanVar()
        chk4 = Checkbutton(self.root, text="Toneburst response (61672-3 Electrical Tests Par.16)",
                           variable=self.toneburst_response)
        chk4.pack()
        self.peak_C_sound_level = BooleanVar()
        chk5 = Checkbutton(self.root, text="Peak C sound Level (61672-3 Electrical Tests Par.17)",
                           variable=self.peak_C_sound_level)
        chk5.pack()
        self.overload_indication = BooleanVar()
        chk6 = Checkbutton(self.root, text="Overload Indication (61672-3 Electrical Tests Par.18)",
                           variable=self.overload_indication)
        chk6.pack()
        b = Button(self.root,text='OK',command=self.get_selection)
        b.pack(side='bottom')

    def waitForInput(self):
        self.root.mainloop()
        
    def get_selection(self):
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()


class takeInput(object):
    """Utility class to show popup and get user input string.
    """
    def __init__(self,requestMessage, title=None):
        self.root = Tk()
        if title:
            self.root.title(title)
        self.root.after(1000, lambda: self.e.focus_force())
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
        b = Button(r,text='OK',command=self.gettext)
        b.pack(side='right')
        
    def gettext(self, *args, **kwargs):
        self.string = self.e.get()
        self.root.withdraw()
        self.root.destroy()
        self.root.quit()

    def getString(self):
        return self.string

    def waitForInput(self):
        self.root.bind('<Return>', self.gettext)
        self.root.mainloop()

def getText(requestMessage, title=None):
    """Loop until the user makes a decision and the window is destroyed.
    """
    msgBox = takeInput(requestMessage, title=title)
    msgBox.waitForInput()
    return msgBox.getString().strip()


def wait(msg, title=None):
    """Wait until any key is pressed. Set Frequency To 2500 Hz and duration to 1 sec
    """
    winsound.Beep(2500, 1000)
    Tk().wm_withdraw() #to hide the main window
    tkMessageBox.showinfo(title if title else "Calibration", msg)
    
    
"""
copied duplicate code, TODO delete it.
class takeInput(object):
    Utility class to show popup and get user input string.
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
    # Wait until any key is pressed.
    
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    Tk().wm_withdraw() #to hide the main window
    tkMessageBox.showinfo("Calibration",msg)
"""