import tkinter as Tk
import socket

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

        self.captureMode = CaptureModeUI()
        
        self.sensorMode = SensorModeUI()
        
        self.gallery = GalleryUI()
        #self.galleryFrame = self.gallery.initializeGallery()

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
        

def main():
    global menubar

    # Step 1
    #      Create our top level window, with a menu bar
    root = Tk.Tk()
   # root.title("PixelinkPreview")
    
    root.attributes('-alpha',0.0)
    root.iconify()
    root.overrideredirect(True)
    root.geometry("%dx%d+%d+%d" % (800, 200,0,300))

   # menubar = Tk.Menu(root)
   # filemenu = Tk.Menu(menubar, tearoff=0)
   # filemenu.add_command(label="Exit", command=root.quit)
   # menubar.add_cascade(label="File", menu=filemenu)
   # root.config(menu=menubar)

    ui = UserInterfaceInit(root)

    dashboardFrame = ui.getDashboardFrame()

    hCamera = ui.hCamera

    panelList = [dashboardFrame]

    buttonframe = Tk.Frame(root)
    container = Tk.Frame(root)
    buttonframe.pack(side="top", fill="x", expand=False)
    container.pack(side="top", fill="both", expand=True)

    dashboardFrame.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
   # captureModeFrame.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

    b1 = Tk.Button(buttonframe, text="Dashboard", command=dashboardFrame.lift,
                   font=("Courier", 9))
    
    b2 = Tk.Button(buttonframe, text="Capture Mode",
                   command=lambda: ui.captureMode.initializeCaptureMode(),
                   font=("Courier", 9))
    
    b3 = Tk.Button(buttonframe, text="Sensor Mode",
                   command=lambda: ui.sensorMode.initializeSensorMode(),
                   font=("Courier", 9))
    
    b4 = Tk.Button(buttonframe, text="Gallery",  font=("Courier", 9),
                   command=lambda: ui.gallery.initializeGallery())
    
   # b5 = Tk.Button(buttonframe, text="Dashboard", font=("Courier", 9))
    b6 = Tk.Button(buttonframe, text="Diagnostics",  font=("Courier", 9))
    b7 = Tk.Button(buttonframe, text='Close',
                   command=lambda: ui.close(root),
                   font=("Courier", 9))
    b8 = Tk.Button(buttonframe, text='Stream',
                   command=lambda: ui.dashboard.startStream(),
                   font=("Courier", 9))

    b1.pack(side="left")
    b2.pack(side="left")
    b3.pack(side="left")
    b4.pack(side="left")
  #  b5.pack(side="left")
    b6.pack(side="left")
    b7.pack(side="right")
    b8.pack(side='right')
    
    ui.dashboard.turnOffLEDS()
    dashboardFrame.lift()

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