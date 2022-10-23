"""
Main_UI.py
Description: Main module where all other UI modules get initialized and started

by: Sofia Saavedra
"""

import tkinter as Tk
import socket

#from RPi import GPIO

from DashboardUI import DashboardUI
from CaptureModeUI import CaptureModeUI
from SensorModeUI import SensorModeUI
from GalleryUI import GalleryUI

#from pixelinkWrapper import *
import time

NEXT_BTN_GPIO = 16
EXIT_BTN_GPIO = 21
SELECT_BTN_GPIO = 20
PICTURE_BTN_GPIO = 26

class UserInterfaceInit:
    def __init__(self, root:Tk):
        """
        Constructor for the UserInterfaceInit class. This class initializes
        the various panels/modules of the UI.

        :param root: the reference to the main TK window.

        """
        
        # set the index of the current window. This index tells what will be the current active window.
        self.index = 0
        # True if a window is open. False otherwise. A window will be open when a specific view is opened, example, 
        # SensorModeUI, CaptureModeUI, etc.
        self.openWindow = False

        # initialize capture settings panel. Used to modify camera settings.
        self.captureMode = CaptureModeUI()
        
        # initialize Sensor panel. Used to modify sensor settings.
        self.sensorMode = SensorModeUI()
        
        # initialize Gallery panel. Used to view images taken
        self.gallery = GalleryUI()
        
        # array that holds the different Panels/windows that we can go through. We are going to use this in order to 
        # iterate through the panels
        self.windows = [self.captureMode, self.sensorMode, self.gallery ]
        # set the amount of menus or panels that we can iterate through
        self.totalMenus = 3

        # initialize DashboardUI. Contains the main dashboard with the camera previews and sensor readings.
        self.dashboard = DashboardUI(root)
        
        # set the ip of the device we want to connect to. In this case, we want to connect to a 
        # Tiva microcontroller to request sensor values.
        self.host = '169.254.153.173'

        # Set the port we would like to connect to.
        self.port = 23

        # establish communication with a desired device. Uses the ip and port that we set up previously.
        self.conn = self.establishCommunication()

        # Initialize dashboard and get back the reference to this dahsboard and the cameras.
        self.dashboardFrame, \
        self.hCamera = self.dashboard.initializeDashboard(
            self.captureMode,
            self.sensorMode,
            self.captureMode.captureModeText,
            self.conn)

    def getDashboardFrame(self) -> Tk.Frame: 
        """Returns the dashboard frame.

        :return Tk.Frame: dashboard frame
        """
        return self.dashboardFrame
    
    def establishCommunication(self) -> None:
        """Establishes communication with whatever ip and port we set on the constructor

        """
        try:
            # creates the socket we will be connecting to
            device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect to the socket
            device_socket.connect((self.host, self.port))
            
            # return the socket 
            return device_socket
        except:
            return 0
    
    def close(self, root:Tk) -> None:
        """
        Function that closes our program and its windows.
        """
        # close the cameras
        self.dashboard.cameraControl.cleanUpCameras(self.hCamera)

        # destroy the UI window
        root.destroy()
    
    def next_window_handler(self, gpio_source:int) -> None:
        """Function that handles iterating to the next window in our defined array of windows.

        :param gpio_source: Number of the gpio that triggered this callback function
        """

        # lets print out the gpio that triggered this call
        print("Triggered GPIO: " + str(gpio_source))
       
        # if the source for this callback is the gpio we have assigned to the "next" button or "next" trigger
        if gpio_source == NEXT_BTN_GPIO:
            # if there is a window already open, close the current window
            if self.openWindow is True:
                (self.windows[self.index]).closeWindow()
            
            # increase the index 
            self.index += 1
            # print the current index of the window
            print("Switched to Index: " + str(self.index))

            # if the index is higher than the total amount of menus or windows we have, reset it back to zero
            if self.index >= self.totalMenus:
                self.index = 0

            # initialize the new window
            (self.windows[self.index]).initialize()

            # set the open window to true, as we just opened a window
            self.openWindow = True
    
    def close_window_handler(self, gpio_source:int) -> None:
        """Function that handles closing the current window

        :param gpio_source: Number of the gpio that triggered this callback function
        """

        # lets print out the gpio that triggered this call
        print("Triggered GPIO: " + str(gpio_source))
        # print the current index of the window
        print("Closing window with Index: " + str(self.index))

        # if the source for this callback is the gpio we have assigned to the "exit" button or "exit" trigger
        if gpio_source == EXIT_BTN_GPIO:
            # if there is an open window
            if(self.openWindow is True):
                # close the currently opened window
                (self.windows[self.index]).closeWindow()
                print("close window with index: " + str(self.index))
                # we currently have no open windows
                self.openWindow = False
                
    
    def take_picture_handler(self, gpio_source:int) -> None:
        """Function that handles the callback to take an picture or frame.

        :param gpio_source: Number of the gpio that triggered this callback function
        """
        # lets print out the gpio that triggered this call
        print("Triggered GPIO: " + str(gpio_source))

        # if the source for this callback is the gpio we have assigned to the "take picture" button 
        # or "take picture" trigger 
        if gpio_source == PICTURE_BTN_GPIO:
            self.dashboard.takePicture()
    
    def closeCameras(self):
        """Close the cameras that we had initialized earlier
        
        """
        previewState = PxLApi.PreviewState.STOP

        # Give preview a bit of time to stop
        time.sleep(0.05)

        # if cameras where initialized previously
        if(self.hCamera):
            PxLApi.setStreamState(self.hCamera, PxLApi.StreamState.STOP)
            PxLApi.uninitialize(self.hCamera)
                
                
def main():
    global menubar

    # Set 1:
    # Create our top level window, with a menu bar
    root = Tk.Tk()
    
    # sets some attributes 
    root.attributes('-alpha',0.0)
    #root.iconify()
    #root.overrideredirect(True)
    root.geometry("%dx%d+%d+%d" % (800, 150,0,305))

    # initialize the User Interface
    ui = UserInterfaceInit(root)
    
    # get the dashboard frame
    dashboardFrame = ui.getDashboardFrame()
    
    #//////////////// Setting up UI widgets /////////////////////////////
    # the font for the buttons
    buttonFont = 7
    # the frame where buttons will be located
    buttonframe = Tk.Frame(root)
    # the container for the dashboard frame
    container = Tk.Frame(root)
    buttonframe.pack(side="left", expand=False)
    container.pack(side="left", fill="both", expand=True)

    dashboardFrame.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
    # captureModeFrame.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

    # b1 = Tk.Button(buttonframe, text="Dashboard", command=dashboardFrame.lift,
    #                    font=("Courier", buttonFont))
    
    # Button for the capture mode window. Clicking on it will open and intiailize
    # the capture mode window
    b2 = Tk.Button(buttonframe, text="Capture Mode",
                   command=lambda: ui.captureMode.initialize(),
                   font=("Courier", buttonFont))
    
    # Button for the sensor mode window. Clicking on it will open and intiailize
    # the sensor mode window
    b3 = Tk.Button(buttonframe, text="Sensor Mode",
                   command=lambda: ui.sensorMode.initialize(),
                   font=("Courier", buttonFont))
    
    # Button for the gallery mode window. Clicking on it will open and intiailize
    # the gallery mode window
    b4 = Tk.Button(buttonframe, text="Gallery",  font=("Courier", buttonFont),
                   command=lambda: ui.gallery.initialize())
    
    # Button for the Diagnostics mode window. diagnostics is not currently implemented
    # TODO: implement a diagnostics window where the user may see the current state of
    # the system.
    b6 = Tk.Button(buttonframe, text="Diagnostics",  font=("Courier", buttonFont))

    # Button to close the windows.
    b7 = Tk.Button(buttonframe, text='Close',
                   command=lambda: ui.close(root),
                   font=("Courier", buttonFont))

    # Button to start the stream from the cameras
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

    try:
        GPIO.setmode(GPIO.BCM)
        
        # sets up the gpio for exiting or closing the current window
        GPIO.setup(EXIT_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Adds an event callback that fires when a down to up signal trigger has been registered in the gpio
        # in this case, the function to exit the currently opened window will be executed
        GPIO.add_event_detect(EXIT_BTN_GPIO, GPIO.FALLING, callback=lambda x : ui.close_window_handler(x), bouncetime=200)
        
        GPIO.setup(NEXT_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Adds an event callback that fires when a down to up signal trigger has been registered in the gpio
        # in this case, the function to open the next window will be executed
        GPIO.add_event_detect(NEXT_BTN_GPIO, GPIO.FALLING, callback=lambda x : ui.next_window_handler(x), bouncetime=200)
    
        GPIO.setup(PICTURE_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Adds an event callback that fires when a down to up signal trigger has been registered in the gpio
        # in this case, the function to take a picture will be executed
        GPIO.add_event_detect(PICTURE_BTN_GPIO, GPIO.FALLING, callback=lambda x : ui.take_picture_handler(x), bouncetime=200)

    except:
        print("error initiating hall effect GPIO")
    
     #/////////////////////////////////////////////
    
    # turns of the LED ring
    ui.dashboard.turnOffLEDS()
    dashboardFrame.lift()

    # Step 4
    # Call the start the UI -- it will only return on Window exit
    root.mainloop()
    
    ui.dashboard.turnOffLEDS()
    ui.dashboard.stopEvent.set()

    # Step 5
    # The user has quit the appliation, shut down the preview and stream
    ui.closeCameras()


if __name__ == "__main__":
    main()