import tkinter as Tk
import socket

from RPi import GPIO

from DashboardUI import DashboardUI
from CaptureModeUI import CaptureModeUI
from SensorModeUI import SensorModeUI
from GalleryUI import GalleryUI

from pixelinkWrapper import *
import time


class UserInterfaceInit:
    def __init__(self, root):
        
        self.host = '169.254.153.173'
        self.port = 23
        
        self.index = 0
        self.openWindow = False

        self.captureMode = CaptureModeUI()
        
        self.sensorMode = SensorModeUI()
        
        self.gallery = GalleryUI()
        
        self.windows = [self.captureMode, self.sensorMode, self.gallery ]
        self.totalMenus = 3

        self.dashboard = DashboardUI(root)
        self.conn = self.establishCommunication()

        self.dashboardFrame, \
        self.hCamera = self.dashboard.initializeDashboard(self.captureMode,
                                                          self.sensorMode,
                                                          self.captureMode.captureModeText,
                                                          self.conn
                                                          )

    def getDashboardFrame(self):
        return self.dashboardFrame
    
    def establishCommunication(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            return s
        except:
            return 0
    
    def close(self, root):
        self.dashboard.cameraControl.cleanUpCameras(self.hCamera)
        root.destroy()
    
    def next_window_handler(self, x):
        print(x)
        print(self.index)
        if x == 16:
            if self.openWindow is True:
                (self.windows[self.index]).closeWindow()
            self.index += 1
            if self.index >= self.totalMenus:
                self.index = 0
            (self.windows[self.index]).initialize()
            self.openWindow = True
      #  time.sleep(0.5)
    
    def close_window_handler(self, x):
        print(x)
        print(self.index)
        if x == 21:
            if(self.openWindow is True):
                frame = self.windows[self.index]
                frame.closeWindow()
                print("close")
                self.openWindow = False
                
      #  time.sleep(0.5)
    
    def take_picture_handler(self, x):
        print(x)
        print(self.index)
        if x == 26:
            self.dashboard.takePicture()
                
      #  time.sleep(0.8)
                

def main():
    global menubar

    # Step 1
    #      Create our top level window, with a menu bar
    root = Tk.Tk()
   # root.title("PixelinkPreview")
    
    root.attributes('-alpha',0.0)
    #root.iconify()
    #root.overrideredirect(True)
    root.geometry("%dx%d+%d+%d" % (800, 150,0,305))

    ui = UserInterfaceInit(root)

    dashboardFrame = ui.getDashboardFrame()

    hCamera = ui.hCamera

    panelList = [dashboardFrame, root.frame()]
    
    buttonFont = 7

    buttonframe = Tk.Frame(root)
    container = Tk.Frame(root)
    buttonframe.pack(side="left", expand=False)
    container.pack(side="left", fill="both", expand=True)

    dashboardFrame.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
   # captureModeFrame.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

#     b1 = Tk.Button(buttonframe, text="Dashboard", command=dashboardFrame.lift,
#                    font=("Courier", buttonFont))
    
    b2 = Tk.Button(buttonframe, text="Capture Mode",
                   command=lambda: ui.captureMode.initialize(),
                   font=("Courier", buttonFont))
    
    b3 = Tk.Button(buttonframe, text="Sensor Mode",
                   command=lambda: ui.sensorMode.initialize(),
                   font=("Courier", buttonFont))
    
    b4 = Tk.Button(buttonframe, text="Gallery",  font=("Courier", buttonFont),
                   command=lambda: ui.gallery.initialize())
    
   # b5 = Tk.Button(buttonframe, text="Dashboard", font=("Courier", 9))
    b6 = Tk.Button(buttonframe, text="Diagnostics",  font=("Courier", buttonFont))
    b7 = Tk.Button(buttonframe, text='Close',
                   command=lambda: ui.close(root),
                   font=("Courier", buttonFont))
    b8 = Tk.Button(buttonframe, text='Stream',
                   command=lambda: ui.dashboard.startStream(),
                   font=("Courier", buttonFont))

    #b1.pack(side="top")
    b2.pack(side="top")
    b3.pack(side="top")
    b4.pack(side="top")
  #  b5.pack(side="left")
    b6.pack(side="top")
    b7.pack(side="bottom")
    b8.pack(side='bottom')
    
    exit_btn = 21
    next_btn = 16
    select_btn = 20
    picture_btn = 26
    
    try:
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(exit_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(exit_btn, GPIO.FALLING, callback=lambda x : ui.close_window_handler(x), bouncetime=200)
        
        GPIO.setup(next_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(next_btn, GPIO.FALLING, callback=lambda x : ui.next_window_handler(x), bouncetime=200)
    
        GPIO.setup(picture_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(picture_btn, GPIO.FALLING, callback=lambda x : ui.take_picture_handler(x), bouncetime=200)

    except:
        print("error initiating hall effect GPIO")
    
    ui.dashboard.turnOffLEDS()
    dashboardFrame.lift()
    
    #(root.frame()).lift()

    # Step 4
    #      Call the start the UI -- it will only return on Window exit
    root.mainloop()
    
    ui.dashboard.turnOffLEDS()
    ui.dashboard.stopEvent.set()

    # Step 5
    #      The user has quit the appliation, shut down the preview and stream
    previewState = PxLApi.PreviewState.STOP

    # Give preview a bit of time to stop
    time.sleep(0.05)

    PxLApi.setStreamState(hCamera, PxLApi.StreamState.STOP)

    PxLApi.uninitialize(hCamera)


if __name__ == "__main__":
    main()