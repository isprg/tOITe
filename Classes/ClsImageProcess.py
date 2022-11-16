class ClsImageProcess:
    def __init__(self, cLogger, cImageSensor, cWindow):
        self.logger = cLogger
        self.sensor = cImageSensor
        self.window = cWindow
        self.sCounter = 0

    def __del__(self):
        self.finalize()

    def finalize(self):
        self.termProcess()

    def termProcess(self):
        pass

    def createWindows(self):
        self.window.createWindows()

    def closeWindows(self):
        self.window.closeWindows()

    def clearWindowText(self):
        self.window.initTextParams()

    def execute(self):
        self.imSensor = self.sensor.read()
        result = self.process()
        tplWindowNames = self.window.getWindowNames()
        for strWindowName in tplWindowNames:
            self.window.imshow(strWindowName, self.imProcessed)
        return result

    def process(self):
        self.imProcessed = self.imSensor
        return 0


if __name__ == "__main__":
    import os
    import cv2
    from ClsLogger import ClsLogger
    from ClsImageProcess import ClsImageProcess
    from ClsImageSensor import ClsImageSensor
    from ClsWindow import ClsWindow

    if os.name == 'nt':
        strPlatform = 'WIN'
    else:
        strPlatform = 'JETSON'

    sCameraNumber = 0
    sSensorWidth = 640
    sSensorHeight = 480
    sMonitorWidth = 1920
    sMonitorHeight = 1280
    tplWindowNames = ("full",)
    blSensorFlip = False
    blMonitorFlip = True

    cLogger = ClsLogger("test-ClsImageProcess")

    cImageSensor = ClsImageSensor(
        strPlatform, sCameraNumber, sSensorWidth, sSensorHeight, blSensorFlip,
    )
    sWidthInput, sHeightInput = cImageSensor.getImageSize()

    cWindow = ClsWindow(tplWindowNames, blMonitorFlip)
    cWindow.prepareFullScreen(
        sMonitorWidth, sMonitorHeight, sWidthInput, sHeightInput
    )
    cWindow.createWindows()

    cProc = ClsImageProcess(cLogger, cImageSensor, cWindow)
    cProc.createWindows()

    while True:
        cProc.execute()
        sKey = cv2.waitKey(1) & 0xFF
        if sKey == ord("q"):
            cProc.finalize()
            cImageSensor.finalize()
            cWindow.finalize()
            break
