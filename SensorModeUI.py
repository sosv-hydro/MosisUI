import tkinter as tki

class SensorModeUI:
    def __init__(self):
        
         # initialize the root window and image
        self.sensorModeRBVar = tki.IntVar()
        self.PH_RB = tki.IntVar()
        self.PH_RB = tki.IntVar()
        self.master_panel = None
        
        self.PH_sensor = tki.IntVar()
        self.Press_sensor = tki.IntVar()
        self.Lumin_sensor = tki.IntVar()
        self.Temp_sensor = tki.IntVar()
        
        self.RB_Press = None
        self.RB_Temp = None
        self.RB_PH = None
        self.RB_Lumin = None
        
        self.test = True
        
        self.PH_sensor.set(1) 
        self.Press_sensor.set(1)
        self.Lumin_sensor.set(1)
        self.Temp_sensor.set(1)
        
    def initializeSensorMode(self):  
        root = tki.Toplevel()
        root.geometry("%dx%d+%d+%d" % (600, 600, 0, 0))
        root.overrideredirect(True)

        self.master_panel = tki.Frame(root, bg='#46637B',height=600, width=600)
        self.master_panel.pack(fill="both")
        
        ocusis_label = tki.Label(self.master_panel, text= "MOSIS", bg='#46637B', fg='white', font=("Courier", 24))
        ocusis_label.pack(fill="both", padx=20, pady=20)
        
        #----------------- Firstmost panel -------------------------------
        panel1 = tki.Frame(self.master_panel, bg='#46637B')
        panel1.pack(fill="both", padx=10, pady=10)
        
        capMode_label = tki.Label(panel1, text= "Sensor Mode ", bg='#46637B', fg='black', font=("Courier", 24))
        capMode_label.pack(side="left",fill="both", padx=20, pady=20)
        
        back_button = tki.Button(panel1, text= "Back",
                                 command=lambda : self.closeWindow(root))
        back_button.pack(side = "right", fill="both", padx=5, pady=5)
        
        fill_label = tki.Label(self.master_panel, text= "", height=1, bg="grey")
        fill_label.pack(fill="x", padx=5, pady=5)
        
        # ---------------- Second Panel ----------------------------------
        panel2 = tki.Frame(self.master_panel, bg='#84A1B9')
        panel2.pack(fill="both", padx=20, pady=20)
        
        actCams_label = tki.Label(panel2, text= "Active Sensors: ", bg='#84A1B9', fg='white', font=("Courier", 14))
        actCams_label.pack(side="left",fill="both", padx=2, pady=10)
        
        self.RB_PH = tki.Checkbutton(panel2, text="PH" , bg='#46637B', variable=self.PH_sensor, selectcolor='red',onvalue = 1, offvalue = 0, 
                             fg='white', font=("Courier", 12), command=self.togglePH)
        self.RB_PH.pack(side="right",fill="both", padx=2, pady=10)
        if(self.PH_sensor.get() == 1):
            self.RB_PH.select()
        
        self.RB_Temp = tki.Checkbutton(panel2, text="Temp", bg='#46637B', variable=self.Temp_sensor, selectcolor='red',onvalue = 1, offvalue = 0,
                             fg='white', font=("Courier", 12))
        self.RB_Temp.pack(side="right",fill="both", padx=2, pady=10)
        if(self.Temp_sensor.get() == 1):
            self.RB_Temp.select()
        
        self.RB_Press = tki.Checkbutton(panel2, text="Press", bg='#46637B', variable=self.Press_sensor, onvalue = 1, offvalue = 0,selectcolor='red',
                             fg='white', font=("Courier", 12))
        self.RB_Press.pack(side="right",fill="both", padx=2, pady=10)
        if(self.Press_sensor.get() == 1):
            self.RB_Press.select()
        
        self.RB_Lumin = tki.Checkbutton(panel2, text="Lumin", bg='#46637B', variable=self.Lumin_sensor, onvalue = 1, offvalue = 0, selectcolor='red',
                             fg='white', font=("Courier", 12))
        self.RB_Lumin.pack(side="right",fill="both", padx=2, pady=10)
        if(self.Lumin_sensor.get() == 1):
            self.RB_Lumin.select()
        
        mode_label = tki.Label(self.master_panel, text= "Mode: ", bg='#46637B', height=2, fg='white', font=("Courier", 14))
        mode_label.pack(fill="x", padx=2, pady=2)
        
         # ---------------- Third Panel ----------------------------------
         
        panel3 = tki.Frame(self.master_panel, bg='#84A1B9')
        panel3.pack(side="top",fill="both", padx=20, pady=10)
        
        singleModeRB = tki.Radiobutton(panel3, text="Single", bg='#46637B', variable=self.sensorModeRBVar, value=int(1),selectcolor='red',
                                       fg='white', font=("Courier", 12) )
        singleModeRB.pack(side="left", fill="both", padx=5, pady=10)
        
        # ---------------- Fourth Panel ----------------------------------
        
        panel5 = tki.Frame(self.master_panel, bg='#84A1B9')
        panel5.pack(side="top",fill="both", padx=20, pady=10)
        
        timeLapseRB = tki.Radiobutton(panel5, text="Time Lapse", bg='#46637B', variable=self.sensorModeRBVar, value=int(2),selectcolor='red',
                                      fg='white', font=("Courier", 12))
        timeLapseRB.pack(side="left", fill="both", padx=5, pady=10)
        
        intervalSB = tki.Spinbox(panel5, from_=0, to=5, bg='#46637B', width= 2, fg='white', font=("Courier", 12) )
        intervalSB.pack(side="right", fill="both", padx=10, pady=5)
        
        interval_label = tki.Label(panel5, text= "Interval:", bg='#84A1B9', height=2, fg='white', font=("Courier", 14))
        interval_label.pack(side="right",fill="x", padx=2, pady=2)
        
        stepSB = tki.Spinbox(panel5, from_=0, to=5, bg='#46637B', width= 2, fg='white', font=("Courier", 12) )
        stepSB.pack(side="right", fill="both", padx=10, pady=5)
        
        step_label = tki.Label(panel5, text= "Step:", bg='#84A1B9', fg='white', font=("Courier", 14))
        step_label.pack(side="right",fill="x", padx=2, pady=2)
        
        # ---------------- Sixth Panel ----------------------------------
        
        panel6 = tki.Frame(self.master_panel, bg='#84A1B9')
        panel6.pack(side="top",fill="both", padx=20, pady=10)
        
        imageStackingRB = tki.Radiobutton(panel6, text="Set Time Lapse as set in camera mode",
                                          variable=self.sensorModeRBVar, value=int(3), bg='#46637B', fg='white', font=("Courier", 12), selectcolor='red')
        imageStackingRB.pack(side="left", fill="both", padx=2, pady=10)

        fill_label2 = tki.Label(self.master_panel, bg='#46637B', height=2)
        fill_label2.pack(side="top",fill="both", padx=20, pady=10)
        
        return self.master_panel
    
    def closeWindow(self, root):
        root.destroy()
    
    def getTimeIntervalValues(self):
        return self.sensorModeRBVar.get()
    
    def toggleLumin(self):
        print("toggle lumin")
       #self.RB_Lumin.toggle()
        print(self.Lumin_sensor.get())
    
    def togglePH(self):
        print("toggle PH")
      #  self.RB_PH.toggle()
        print(self.PH_sensor.get())
    
    def toggleTemp(self):
       # self.RB_Temp.toggle()
        print(self.Temp_sensor.get())
    
    def togglePress(self):
       # self.RB_Press.toggle()
        print(self.Press_sensor.get()) 
    
    def getActiveSensors(self):
        sensorList = {"PH":self.PH_sensor.get(), "TEMP":self.Temp_sensor.get(),
                      "PRES":self.Press_sensor.get(), "LUMIN":self.Lumin_sensor.get()}
#         if self.test == False:
#             self.PH_sensor.set(1) 
#             self.Press_sensor.set(1)
#             self.Lumin_sensor.set(1)
#             self.Temp_sensor.set(1)
#         else:
#             self.PH_sensor.set(0) 
#             self.Press_sensor.set(0)
#             self.Lumin_sensor.set(0)
#             self.Temp_sensor.set(0)
#         self.test = not self.test
        return sensorList
