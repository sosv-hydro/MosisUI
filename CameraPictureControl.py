"""
CameraPictureControl.py
Code to capture an image from a Pixelink camera and save the encoded image to folder as a file.
"""

#from pixelinkWrapper import *
from ctypes import *
import os
from datetime import datetime
import time

SUCCESS = 0
FAILURE = 1

class CameraPictureControl():

    def __init__(self, picFormat=PxLApi.ImageFormat.JPEG ):
        """Constructor
        """
        # set the image format
        self.imageFormat = picFormat

    def get_snapshot(self, hCamera, fileName) -> bool:
        """
        Get a snapshot from the camera, and save to a file.

        :param hCamera: reference to the camera we are using to take these images
        :param fileName: filename onto which we will save the image
        :return bool: true if the function was a success, false otherwise
        """
        assert 0 != hCamera
        assert fileName
        
        counter = 0

        # Determine the size of buffer we'll need to hold an image from the camera
        rawImageSize = self.determine_raw_image_size(hCamera[0])
        if 0 == rawImageSize:
            return FAILURE

        # Create a buffer to hold the raw image
        rawImage = create_string_buffer(rawImageSize)

        # if we actually have data in the buffer, continue
        if 0 != len(rawImage):
            
            for i in range(len(hCamera)):
                # Capture a raw image. The raw image buffer will contain image data on success.
                ret = self.get_raw_image(hCamera[i], rawImage)
                if PxLApi.apiSuccess(ret[0]):
                    frameDescriptor = ret[1]

                    print("took picture")

                    assert 0 != len(rawImage)
                    assert frameDescriptor
                    #
                    # Do any image processing here
                    #

                    print("format picture")

                    # Encode the raw image into something displayable
                    ret = PxLApi.formatImage(rawImage, frameDescriptor, self.imageFormat)
                    print("formatted picture")

                    if SUCCESS == ret[0]:
                        formatedImage = ret[1]
                        # Save formated image into a file

                        print("saving picture")
                        fileName = fileName + "_" + str(i)

                        if self.save_image_to_file(fileName, formatedImage) == SUCCESS:
                            return SUCCESS

            return FAILURE

    def getBurstSnapshot(self, burstNumber:int, hCamera, burstInterval:int=0) -> bool: 
        """Takes a number of pictures in succession, or as a burst. The amount of images
        taken is directly related to the burstNumber stiputlated on the parameter provided.

        :param burstNumber: number of images to take at once
        :param hCamera: reference to the camera we are using to take these images
        :return bool: true if the burst snapshot was a success, false otherwise
        """
        counter = 0

        try:
            while counter < burstNumber:
                fileName = "burst" + str(counter) +"_"+ str(datetime.now().strftime("%Y_%m_%d %H_%M_%S"))
                # Get a snapshot and save it to a folder as a file
                retVal = self.get_snapshot(hCamera, fileName)
                counter += 1
            return SUCCESS
        except:
            return FAILURE

    def getIntervalSnapshot(self, hCamera, total_interval_min, steps) -> bool:
        """Function to take images on a stipulated interval. This interval is directed by the total_inteval_min 
        and the steps parameter

        :param total_interval_min: total time in which to take images
        :param steps: steps on which to take each image. Or the sub interval of the total interval.
        :param hCamera: reference to the camera we are using to take these images
        :return bool: true if the interval snapshot was a success, false otherwise
        """
        counter = 0

        interval_seconds = 60 * total_interval_min
        
        # get the time at this moment as the start time for the total interval and the steps
        start_time = time.time()
        start_step = time.time()

        print("start interval snapshot")
        # the total amount of images to take will be a function of the total interval time and 
        # the steps we want to take inside it.
        total_pictures = interval_seconds / steps

        print("start time: ", start_time)

        try:
            # while the time transpired is less than that specified or the total pictures taken is less
            # than that stipulated before. 
            while time.time() - start_time <= interval_seconds or counter < total_pictures:
               
               # if the step time has been reached, take an image
                if time.time() - start_step >= steps:
                    fileName = "interval" + str(counter) +"_"+ str(datetime.now().strftime("%Y_%m_%d %H_%M_%S"))
                    # Get a snapshot and save it to a folder as a file
                    retVal = self.get_snapshot(hCamera, fileName)
                    counter += 1
                    start_step = time.time()
            return SUCCESS
        except:
            return FAILURE

    def determine_raw_image_size(self, hCamera) -> float:
        """Query the camera for region of interest (ROI), decimation, and pixel format
        Using this information, we can calculate the size of a raw image
        Returns 0 on failure

        :param hCamera: reference to the camera we are using to take these images
        :return float: size of the raw image
        """
        assert 0 != hCamera

        # Get region of interest (ROI)
        ret = PxLApi.getFeature(hCamera, PxLApi.FeatureId.ROI)
        params = ret[2]
        roiWidth = params[PxLApi.RoiParams.WIDTH]
        roiHeight = params[PxLApi.RoiParams.HEIGHT]

        # Query pixel addressing
        # assume no pixel addressing (in case it is not supported)
        pixelAddressingValueX = 1
        pixelAddressingValueY = 1

        ret = PxLApi.getFeature(hCamera, PxLApi.FeatureId.PIXEL_ADDRESSING)
        if PxLApi.apiSuccess(ret[0]):
            params = ret[2]
            if PxLApi.PixelAddressingParams.NUM_PARAMS == len(params):
                # Camera supports symmetric and asymmetric pixel addressing
                pixelAddressingValueX = params[PxLApi.PixelAddressingParams.X_VALUE]
                pixelAddressingValueY = params[PxLApi.PixelAddressingParams.Y_VALUE]
            else:
                # Camera supports only symmetric pixel addressing
                pixelAddressingValueX = params[PxLApi.PixelAddressingParams.VALUE]
                pixelAddressingValueY = params[PxLApi.PixelAddressingParams.VALUE]

        # We can calulate the number of pixels now.
        numPixels = (roiWidth / pixelAddressingValueX) * (roiHeight / pixelAddressingValueY)
        ret = PxLApi.getFeature(hCamera, PxLApi.FeatureId.PIXEL_FORMAT)

        # Knowing pixel format means we can determine how many bytes per pixel.
        params = ret[2]
        pixelFormat = int(params[0])

        # And now the size of the frame
        pixelSize = PxLApi.getBytesPerPixel(pixelFormat)

        return int(numPixels * pixelSize)

    def get_raw_image(self, hCamera, rawImage):
        """
        Capture an image from the camera.

        NOTE: PxLApi.getNextFrame is a blocking call.
        i.e. PxLApi.getNextFrame won't return until an image is captured.
        So, if you're using hardware triggering, it won't return until the camera is triggered.
        Returns a return code with success and frame descriptor information or API error
        """

        assert 0 != hCamera
        assert 0 != len(rawImage)

        MAX_NUM_TRIES = 4

        # Put camera into streaming state so we can capture an image
        ret = PxLApi.setStreamState(hCamera, PxLApi.StreamState.START)
        if not PxLApi.apiSuccess(ret[0]):
            return FAILURE

        # Get an image
        # NOTE: PxLApi.getNextFrame can return ApiCameraTimeoutError on occasion.
        # How you handle this depends on your situation and how you use your camera.
        # For this sample app, we'll just retry a few times.
        ret = (PxLApi.ReturnCode.ApiUnknownError,)

        for i in range(MAX_NUM_TRIES):
            ret = PxLApi.getNextFrame(hCamera, rawImage)
            if PxLApi.apiSuccess(ret[0]):
                break

        return ret

    def save_image_to_file(self, fileName, formatedImage) -> bool:
        """
        Save the encoded image buffer to a file
        This overwrites any existing file
        :return bool: Returns SUCCESS or FAILURE
        """

        assert fileName
        assert 0 != len(formatedImage)

        # Create a folder to save snapshots if it does not exist
        if not os.path.exists("Media"):
            os.makedirs("Media")
        
        if not os.path.exists("Media/Images"):
            os.makedirs("Media/Images")

        filepass = "Media/Images/" + fileName + ".jpg"
        # Open a file for binary write
        file = open(filepass, "wb")
        if None == file:
            return FAILURE
        numBytesWritten = file.write(formatedImage)
        file.close()
        print("picture saved")

        if numBytesWritten == len(formatedImage):
            return SUCCESS

        return FAILURE


# def main():
#     picControl = CameraPictureControl()

#     filenameJpeg = "snapshot.jpg"

#     ret = PxLApi.initialize(0)
#     if not PxLApi.apiSuccess(ret[0]):
#         return 1
#     hCamera = ret[1]

#     # Get a snapshot and save it to a folder as a file
#     retVal = picControl.get_snapshot(hCamera, filenameJpeg)

#     # Done capturing, so no longer need the camera streaming images.
#     # Note: If ret is used for this call, it will lose frame descriptor information.
#     PxLApi.setStreamState(hCamera, PxLApi.StreamState.STOP)

#     # Tell the camera we're done with it.
#     PxLApi.uninitialize(hCamera)

#     if SUCCESS != retVal:
#         print("ERROR: Unable to capture an image")
#         return FAILURE

#     return SUCCESS


# if __name__ == "__main__":
#     main()