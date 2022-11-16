import cv2
import numpy as np

from Classes.ClsImageProcess import ClsImageProcess


class ClsImageProcessQR(ClsImageProcess):
    def setAnswer(self, strAnswer):
        self.strAnswer = strAnswer

    def process(self):
        isFound = False
        imGray = cv2.cvtColor(self.imSensor, cv2.COLOR_BGR2GRAY)
        qr = cv2.QRCodeDetector()
        data, points, straight_qrcode = qr.detectAndDecode(imGray)
        if self.strAnswer in data:
            pts = points.astype(np.int32)
            self.imProcessed = cv2.polylines(
                self.imSensor, [pts], True, (0, 0, 255), 2, cv2.LINE_AA)
            self.sCounter = self.sCounter + 1
            if self.sCounter > 5:
                self.sCounter = 0
                isFound = True
        else:
            self.imProcessed = self.imSensor

        return isFound


if __name__ == '__main__':
    import cv2
    import os
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

    cLogger = ClsLogger("test-ClsImageProcessQR")

    cImageSensor = ClsImageSensor(
        strPlatform, sCameraNumber, sSensorWidth, sSensorHeight, blSensorFlip,
    )
    sWidthInput, sHeightInput = cImageSensor.getImageSize()

    cWindow = ClsWindow(tplWindowNames, blMonitorFlip)
    cWindow.prepareFullScreen(
        sMonitorWidth, sMonitorHeight, sWidthInput, sHeightInput
    )
    cWindow.createWindows()

    cProc = ClsImageProcessQR(cLogger, cImageSensor, cWindow)
    cProc.setAnswer('LenaKnows')
    cProc.createWindows()

    while True:
        cProc.execute()
        sKey = cv2.waitKey(1) & 0xFF
        if sKey == ord('q'):
            cProc.finalize()
            cImageSensor.finalize()
            cWindow.finalize()
            break
