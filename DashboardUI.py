"""
previewWithTk.py
Simple sample application demostrating the use of the API Preview function,
embedded within a Tknter window
"""
from pixelinkWrapper import *
from ctypes import *
import ctypes.wintypes
import tkinter as Tk
import time
import win32api, win32con

from CameraControl import CameraControl

from CameraPictureControl import CameraPictureControl

SINGLE = 1
BURST = 2
INTERVAL = 3
IMAGESTACK = 4

class DashboardUI:

    def __init__(self, root):
        self.focusSNum = Tk.IntVar()
        self.exposureSNum = Tk.DoubleVar()
        self.saturationSNum = Tk.IntVar()
        self.gainSNum = Tk.DoubleVar()
        self.picSuccess = Tk.StringVar()

        self.captureModeClass = None

        self.captureModeDict = None

        self.hCamera = None
        self.cameraControl = None
        self.cameraPictureControl = CameraPictureControl()

        self.topHwnd = None
        self.root = root


    def winResizeHandler(self, event):
        # The user has resized the window.  Also resize the preview so that the preview will scale to the new window size
        PxLApi.setPreviewSettings(self.hCamera, "", PxLApi.WindowsPreview.WS_VISIBLE | PxLApi.WindowsPreview.WS_CHILD, 0, 0,
                                  event.width, event.height, self.topHwnd)

    def configureLowerDashboardPanel(self, master_panel):

        lower_panel = Tk.Frame(master_panel, bg='#46637B')
        lower_panel.pack(side="bottom", padx=2, pady=2)

        # panel for the scales
        scale_panel = Tk.Frame(lower_panel, bg='#004000')
        scale_panel.pack(side="left", fill="both", padx=2, pady=2)

        params_label = Tk.Label(scale_panel, text="Camera Frame params: ")
        params_label.pack(side="top", fill="x", padx=5, pady=5)

        # panel for the scales
        sub_scale_panelL = Tk.Frame(scale_panel, bg='#004000')
        sub_scale_panelL.pack(side="left", fill="both", padx=5, pady=5)

        # panel for the scales
        sub_scale_panelR = Tk.Frame(scale_panel, bg='#004000')
        sub_scale_panelR.pack(side="left", fill="both", padx=5, pady=5)

        focusScale = Tk.Scale(sub_scale_panelL, from_=2, to=46000, resolution=5, orient=Tk.HORIZONTAL, width=5,
                              troughcolor="#004000", bg='#84A1B9', label="Focus", variable=self.focusSNum,
                              command=lambda x: self.cameraControl.setFocus(self.hCamera, self.focusSNum.get(), "manual"))
        focusScale.pack(side="top", fill="none", padx=2, pady=2)

        exposureScale = Tk.Scale(sub_scale_panelL, from_=0.00000002, to=0.5, resolution=0.00000001, orient=Tk.HORIZONTAL, width=5,
                                  troughcolor="#004000", bg='#84A1B9', label="Exposure", variable=self.exposureSNum,
                              command=lambda x: self.cameraControl.setExposure(self.hCamera, self.exposureSNum.get(), "manual"))
        exposureScale.pack(side="top", fill="none", padx=2, pady=2)

        saturationScale = Tk.Scale(sub_scale_panelR, from_=0, to=200, resolution=1, orient=Tk.HORIZONTAL, width=5,
                                    troughcolor="#004000", bg='#84A1B9', label="Saturation",variable=self.saturationSNum,
                              command=lambda x: self.cameraControl.setSaturation(self.hCamera, self.saturationSNum.get(), "manual"))
        saturationScale.pack(side="top", fill="none", padx=2, pady=2)

        gainScale = Tk.Scale(sub_scale_panelR, from_=1, to=24, resolution=0.5, orient=Tk.HORIZONTAL, width=5,
                                    troughcolor="#004000", bg='#84A1B9', label="Gain",variable=self.gainSNum,
                              command=lambda x: self.cameraControl.setGain(self.hCamera, self.gainSNum.get(), "manual"))
        gainScale.pack(side="top", fill="none", padx=2, pady=2)

        # ---------------- Mode configuration PANEL----------------------------------#

        # panel for led / mode info
        modeConfig_panel = Tk.Frame(lower_panel, bg='#004000', width=50, height=50)
        modeConfig_panel.pack(side="left", fill="both", padx=2, pady=2)

        modeConfig_panelU = Tk.Frame(modeConfig_panel, bg='#004000', width=25, height=50)
        modeConfig_panelU.pack(side="top", fill="x", padx=5, pady=5)

        modeConfig_panelL = Tk.Frame(modeConfig_panel, bg='#004000', width=25, height=50)
        modeConfig_panelL.pack(side="top", fill="x", padx=5, pady=5)

        modeConfig_panelSnap = Tk.Frame(modeConfig_panel, bg='#004000', width=25, height=50)
        modeConfig_panelSnap.pack(side="top", fill="x", padx=5, pady=5)

        btnAutoF = Tk.Button(modeConfig_panelSnap, text="Auto Focus",
                             command=lambda: self.cameraControl.setFocus(self.hCamera))
        btnAutoF.pack(side="left", fill="none", padx=2, pady=2)

        # create a button, that when pressed, will take the current
        # frame and save it to file
        btn = Tk.Button(modeConfig_panelSnap, text="Snapshot!",
                        command=lambda: self.takePicture())
        btn.pack(side="left", fill="none", padx=10, pady=2)

        mode1_label = Tk.Label(modeConfig_panel, text="", bg='#46637B', fg='white',
                                textvariable=self.picSuccess, width=5, font=("Courier", 9))
        mode1_label.pack(side="bottom", fill="x", padx=2, pady=2)

        mode_label = Tk.Label(modeConfig_panelU, text="Mode: ", width=10)
        mode_label.pack(side="left", fill="both", padx=2, pady=2)

        mode_var_label = Tk.Label(modeConfig_panelU, textvariable=self.captureModeVar, bg='#46637B', fg='white', width=10)
        mode_var_label.pack(side="left", fill="both", padx=2, pady=2)

        selected_LED = Tk.Label(modeConfig_panelL, text="LED: ", bg="#84A1B9", width=10, font=("Courier", 7))
        selected_LED.pack(side="left", fill="both", padx=2, pady=2)

        R1 = Tk.Radiobutton(modeConfig_panelL, text="UV", bg='#46637B', selectcolor='red',
                             value=int(1),
                             fg='white', font=("Courier", 8))
        R1.pack(side="left", fill="both", padx=5, pady=10)

        R2 = Tk.Radiobutton(modeConfig_panelL, text="NIR", bg='#46637B', selectcolor='red',
                             value=int(2),
                             fg='white', font=("Courier", 8))
        R2.pack(side="left", fill="both", padx=5, pady=10)

        R3 = Tk.Radiobutton(modeConfig_panelL, text="FS_White", bg='#46637B', selectcolor='red',
                             value=int(3),
                             fg='white', font=("Courier", 8))
        R3.pack(side="left", fill="both", padx=5, pady=10)

        # ---------------- Sensor PANEL----------------------------------#

        # panel for the activated sensors
        sensor_panel = Tk.Frame(lower_panel, bg='#004000', width=50, height=100)
        sensor_panel.pack(side="left", fill="both", padx=2, pady=2)

        act_sensor_label = Tk.Label(sensor_panel, text="Active Sensors", font=("Courier", 10))
        act_sensor_label.pack(side="top", fill="both", padx=5, pady=5)

        sensor_panelU = Tk.Frame(sensor_panel, bg='#004000', width=25)
        sensor_panelU.pack(side="left", fill="both", padx=5, pady=5)

        sensor_panelR = Tk.Frame(sensor_panel, bg='#004000', width=25)
        sensor_panelR.pack(side="left", fill="both", padx=5, pady=5)

        PH_label = Tk.Label(sensor_panelU, text="PH", bg='#84A1B9')
        PH_label.pack(side="top", fill="both", padx=5, pady=5)

        PH_labelvar = Tk.Label(sensor_panelU, text="", bg='white', width=5, font=("Courier", 9))
        PH_labelvar.pack(side="top", fill="both", padx=5, pady=5)

        Pressure_label = Tk.Label(sensor_panelU, text='Pressure', bg='#84A1B9')
        Pressure_label.pack(side="top", fill="both", padx=5, pady=5)

        Pressure_labelvar = Tk.Label(sensor_panelU, text="", bg='white', width=5,
                                      font=("Courier", 9))
        Pressure_labelvar.pack(side="top", fill="both", padx=5, pady=5)

        Temp_label = Tk.Label(sensor_panelR, text="Temp", bg='#84A1B9')
        Temp_label.pack(side="top", fill="both", padx=5, pady=5)

        Temp_labelvar = Tk.Label(sensor_panelR, text="", bg='white', width=5, font=("Courier", 9))
        Temp_labelvar.pack(side="top", fill="both", padx=5, pady=5)

        Lumin_label = Tk.Label(sensor_panelR, text="Lumin", bg='#84A1B9')
        Lumin_label.pack(side="top", fill="both", padx=5, pady=5)

        Lumin_labelvar = Tk.Label(sensor_panelR, text="", bg='white', width=5,
                                   font=("Courier", 9))
        Lumin_labelvar.pack(side="top", fill="both", padx=5, pady=5)

    def takePicture(self):
        ret = None
        mode = self.captureModeVar.get()

        if self.captureModeDict[SINGLE] == mode:
            print("taking single picture")
            ret = self.cameraPictureControl.get_snapshot(self.hCamera, "snapshot")
        elif self.captureModeDict[BURST] == mode:
            print("taking burst picture")

            self.picSuccess.set("Taking Burst pictures.....")
            burstNumber = int(self.captureModeClass.burstSB)
            ret = self.cameraPictureControl.getBurstSnapshot(burstNumber, self.hCamera)
        elif self.captureModeDict[INTERVAL] == mode:
            print("taking interval picture")

            self.picSuccess.set("Taking Interval pictures....")
            time.sleep(2)
            total_interval = int(self.captureModeClass.intervalSB)
            steps = int(self.captureModeClass.stepSB)
            ret = self.cameraPictureControl.getIntervalSnapshot(self.hCamera, total_interval, steps)

        if ret == 0:
            self.picSuccess.set("Picture success!")
        else:
            self.picSuccess.set("Picture error")

    def initializeDashboard(self, captureModeClass, cameraModeVar=None):

        stream_width = 640
        stream_height = 480

        master_panel = Tk.Frame(self.root, bg='#46637B')
        master_panel.pack(anchor="w", expand=False, side="bottom", fill=None)

        # Create class for controling camera features like focus, sharpness, etc.
        self.cameraControl = CameraControl()

        self.captureModeClass = captureModeClass

        self.captureModeDict = captureModeClass.captureModeDict


        # Set up the camera
        self.hCamera = self.cameraControl.setUpCamera()

        if self.hCamera is None:
            return

        # If a StringVar was not provided by the capture mode class, create one
        if cameraModeVar == None:
            self.captureModeVar = Tk.StringVar()
        else:
            self.captureModeVar = cameraModeVar

        # This method configures the lower Panel on the main camera view (dashboard)
        self.configureLowerDashboardPanel(master_panel)

        # Just use all of the camers's current settings.
        # Start the stream
        ret = PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.START)

        if PxLApi.apiSuccess(ret[0]):
            # Start the preview / message pump, as well as the Tknter window resize handler
            self.topHwnd = int(self.root.frame(), 0)

            self.cameraControl.start_preview(stream_width, stream_height, self.hCamera, self.topHwnd)

        return master_panel, self.hCamera


def main():
    global menubar

    # Step 1
    #      Create our top level window, with a menu bar
    topWindow = Tk.Tk()
    topWindow.title("PixelinkPreview")
    topWindow.geometry("%dx%d+0+0" % (820, 655))

    menubar = Tk.Menu(topWindow)
    filemenu = Tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=topWindow.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    topWindow.config(menu=menubar)

    ui = DashboardUI()

    master_panel, hCamera = ui.initializeDashboard(topWindow)

    # Step 4
    #      Call the start the UI -- it will only return on Window exit
    topWindow.mainloop()

    # Step 5
    #      The user has quit the appliation, shut down the preview and stream
    previewState = PxLApi.PreviewState.STOP

    # Give preview a bit of time to stop
    time.sleep(0.05)

    PxLApi.setStreamState(hCamera, PxLApi.StreamState.STOP)

    PxLApi.uninitialize(hCamera)



if __name__ == "__main__":
    main()