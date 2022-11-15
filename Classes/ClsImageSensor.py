import cv2


class ClsImageSensor:
    def __init__(
        self, strPlatform, sCameraNumber, sWidthInput, sHeightInput, sFlipEnable
    ):
        self.active = False
        self.strPlatform = strPlatform
        self.sFlipEnable = sFlipEnable

        if strPlatform == "WIN":
            self.videoCap = cv2.VideoCapture(sCameraNumber, cv2.CAP_DSHOW)
            self.videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, sWidthInput)
            self.videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, sHeightInput)
        elif strPlatform == "RASPI":
            self.videoCap = cv2.VideoCapture(sCameraNumber)
            self.videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, sWidthInput)
            self.videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, sHeightInput)
        elif strPlatform == "JETSON":
            if sFlipEnable == True:
                sFlipMethod = 6
            else:
                sFlipMethod = 2
            GST_STR = self.gstreamer_pipeline(
                30, sFlipMethod, sWidthInput, sHeightInput
            )
            self.videoCap = cv2.VideoCapture(GST_STR, cv2.CAP_GSTREAMER)

        if self.videoCap.isOpened():
            sReturn, imSensor = self.videoCap.read()
            print("W: ", imSensor.shape[1], ", H:", imSensor.shape[0])
            self.sWidth = int(imSensor.shape[1])
            self.sHeight = int(imSensor.shape[0])
            self.active = True

    def __del__(self):
        self.release()

    def Finalize(self):
        self.release()

    def gstreamer_pipeline(self, sFrameRate, sFlipMethod, sWidthInput, sHeightInput):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "appsink max-buffers=1 drop=True"
            # "nvoverlaysink -e"
            % (720, 480, sFrameRate, sFlipMethod, sWidthInput, sHeightInput)
        )

    def getImageSize(self):
        if self.isOpened():
            return self.sWidth, self.sHeight
        else:
            print("No sensor is available.")

    def read(self):
        if self.isOpened():
            sReturn, self.imSensor = self.videoCap.read()
            if self.strPlatform != "JETSON" and self.sFlipEnable == True:
                self.imSensor = cv2.flip(self.imSensor, 1)
            return self.imSensor

    def isOpened(self):
        return self.active

    def release(self):
        self.videoCap.release()
