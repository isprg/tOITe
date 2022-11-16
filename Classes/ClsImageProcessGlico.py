from Classes.ClsImageProcess import ClsImageProcess


class ClsImageProcessGlico(ClsImageProcess):
    def setPoseClass(self, cAppend):
        self.cPose = cAppend

    def showParams(self):
        self.window.setText(0, "Neck : " + str(self.sTiltNeck), (0, 50))
        self.window.setText(1, "Body : " + str(self.sTiltBody), (0, 100))
        self.window.setText(
            2, "RUA  : " + str(self.sTiltRightUpperArm), (0, 150))
        self.window.setText(
            3, "RFA  : " + str(self.sTiltRightForearm), (0, 200))
        self.window.setText(
            4, "LUA  : " + str(self.sTiltLeftUpperArm), (0, 250))
        self.window.setText(
            5, "LFA  : " + str(self.sTiltLeftForearm), (0, 300))
        self.window.setText(6, "Pose : " + str(self.strPose), (0, 350))
        self.window.setText(7, "Still: " + str(self.blStill), (0, 400))

    def process(self):
        self.cPose.searchLandmarks(self.imSensor)
        self.cPose.drawLandmarks()
        self.sTiltNeck = self.cPose.getTiltNeck()
        self.sTiltBody = self.cPose.getTiltBody()
        self.sTiltRightUpperArm = self.cPose.getTiltRightUpperArm()
        self.sTiltRightForearm = self.cPose.getTiltRightForearm()
        self.sTiltLeftUpperArm = self.cPose.getTiltLeftUpperArm()
        self.sTiltLeftForearm = self.cPose.getTiltLeftForearm()
        self.blCrossArms = self.cPose.areArmsCrossed()
        self.blStill = self.cPose.isStationary()
        self.strPose = 'None'

        if self.sTiltLeftForearm < -140 and self.sTiltRightForearm > 140 and \
                self.sTiltLeftUpperArm < -120 and self.sTiltRightUpperArm > 120:
            self.strPose = 'Glico'

        # self.showParams()
        self.imProcessed = self.imSensor

        if self.strPose == 'Glico':
            return True
        else:
            return False


if __name__ == "__main__":
    import os
    import cv2
    from ClsLogger import ClsLogger
    from ClsImageProcess import ClsImageProcess
    from ClsImageSensor import ClsImageSensor
    from ClsWindow import ClsWindow
    from ClsPoseEstimation import ClsPoseEstimation

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

    cLogger = ClsLogger("test-ClsImageProcessGlico")

    cImageSensor = ClsImageSensor(
        strPlatform, sCameraNumber, sSensorWidth, sSensorHeight, blSensorFlip,
    )
    sWidthInput, sHeightInput = cImageSensor.getImageSize()

    cWindow = ClsWindow(tplWindowNames, blMonitorFlip)
    cWindow.prepareFullScreen(
        sMonitorWidth, sMonitorHeight, sWidthInput, sHeightInput
    )
    cWindow.createWindows()

    cPose = ClsPoseEstimation(0.5, 0.5)
    sRatioROI = 0.6
    sWidth, sHeight = cImageSensor.getImageSize()
    cPose.defineROI(sWidth, sRatioROI)

    cProc = ClsImageProcessGlico(cLogger, cImageSensor, cWindow)
    cProc.setPoseClass(cPose)
    cProc.createWindows()

    while True:
        cProc.execute()
        sKey = cv2.waitKey(1) & 0xFF
        if sKey == ord("q"):
            cProc.finalize()
            cPose.finalize()
            cImageSensor.finalize()
            cWindow.finalize()
            break
