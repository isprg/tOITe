import cv2
import numpy as np
import mediapipe as mp


class ClsPoseEstimation():
    def __init__(self, sMinDetectionConfidence, sMinTrackingConfidence):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=sMinDetectionConfidence,
            min_tracking_confidence=sMinTrackingConfidence)
        self.leftPosROI = 0
        self.rightPosROI = 0
        self.isROIdefined = False
        self.vPositionX = np.zeros(33).astype(int)
        self.vPositionY = np.zeros(33).astype(int)
        self.vPositionZ = np.zeros(33)
        self.vVisibility = np.zeros(33)
        self.initDrawParams()
        self.initStationaryParams()

    def __del__(self):
        self.finalize()

    def finalize(self):
        self.pose

    def initDrawParams(self):
        self.sLineWidth = 2
        self.vLineColor = [0, 255, 0]
        self.sCircleRadius = 4
        self.vCircleColor = [0, 0, 255]

    def initStationaryParams(self):
        self.sCountStill = 0
        self.sPositionStationary = 5
        self.sFrameStationary = 5
        self.sRightWristX = 0
        self.sRightWristY = 0
        self.sLeftWristX = 0
        self.sLeftWristY = 0

    def defineROI(self, sImageWidth, ratioROI, strMode):
        sROIWidth = int(sImageWidth * ratioROI)
        if strMode == "CENTER":
            self.leftPosROI = int((sImageWidth - sROIWidth) / 2)
            self.rightPosROI = sImageWidth - self.leftPosROI
        elif strMode == "RIGHT":
            self.leftPosROI = 0
            self.rightPosROI = sROIWidth - 1
        elif strMode == "LEFT":
            self.leftPosROI = sImageWidth - sROIWidth
            self.rightPosROI = sImageWidth - 1
        self.isROIdefined = True

    def setDrawParameters(self, sLineWidth, vLineColor, sCircleRadius, vCircleColor):
        self.sLineWidth = sLineWidth
        self.vLineColor = vLineColor
        self.sCircleRadius = sCircleRadius
        self.vCircleColor = vCircleColor

    def drawLandmarks(self):
        self.drawLine(11, 12)
        self.drawLine(11, 23)
        self.drawLine(12, 24)
        self.drawLine(23, 24)

        for sNumOfMark in range(len(self.vPositionX)):
            if 0 <= self.vPositionX[sNumOfMark] <= self.imInput.shape[1] and \
                    0 <= self.vPositionY[sNumOfMark] <= self.imInput.shape[0]:
                if 11 <= sNumOfMark <= 16 or 23 <= sNumOfMark <= 26:
                    self.drawLine(sNumOfMark, sNumOfMark + 2)
                    cv2.circle(self.imInput,
                               center=(
                                   self.vPositionX[sNumOfMark], self.vPositionY[sNumOfMark]),
                               radius=self.sCircleRadius,
                               color=self.vCircleColor,
                               thickness=-1,
                               lineType=cv2.LINE_4)
                elif 15 <= sNumOfMark <= 18:
                    cv2.circle(self.imInput,
                               center=(
                                   self.vPositionX[sNumOfMark], self.vPositionY[sNumOfMark]),
                               radius=self.sCircleRadius,
                               color=self.vCircleColor,
                               thickness=-1,
                               lineType=cv2.LINE_4)

    def drawLine(self, sNumOfMark1, sNumOfMark2):
        cv2.line(self.imInput,
                 (self.vPositionX[sNumOfMark1], self.vPositionY[sNumOfMark1]),
                 (self.vPositionX[sNumOfMark2], self.vPositionY[sNumOfMark2]),
                 color=self.vLineColor,
                 thickness=self.sLineWidth,
                 lineType=cv2.LINE_4)

    def searchLandmarks(self, imInput):
        self.imInput = imInput
        if self.isROIdefined == False:
            imROI = imInput
        else:
            imROI = imInput[:, self.leftPosROI:self.rightPosROI]

        imROI = cv2.cvtColor(imROI, cv2.COLOR_BGR2RGB)
        imROI.flags.writeable = False
        results = self.pose.process(imROI)
        imROI.flags.writeable = True
        imROI = cv2.cvtColor(imROI, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            sNumOfMark = 0
            for landmark in results.pose_landmarks.landmark:
                self.vPositionX[sNumOfMark] = landmark.x * \
                    imROI.shape[1]+self.leftPosROI
                self.vPositionY[sNumOfMark] = landmark.y*imROI.shape[0]
                self.vPositionZ[sNumOfMark] = landmark.z
                self.vVisibility[sNumOfMark] = landmark.visibility
                sNumOfMark = sNumOfMark + 1
            self.judgeStationary()

    def judgeStationary(self):
        sMinRightX = np.max([0, self.sRightWristX - self.sPositionStationary])
        sMaxRightX = self.sRightWristX + self.sPositionStationary
        sMinRightY = np.max([0, self.sRightWristY - self.sPositionStationary])
        sMaxRightY = self.sRightWristY + self.sPositionStationary
        sMinLeftX = np.max([0, self.sLeftWristX - self.sPositionStationary])
        sMaxLeftX = self.sLeftWristX + self.sPositionStationary
        sMinLeftY = np.max([0, self.sLeftWristY - self.sPositionStationary])
        sMaxLeftY = self.sLeftWristY + self.sPositionStationary

        if sMinRightX < self.vPositionX[16] < sMaxRightX and \
                sMinRightY < self.vPositionY[16] < sMaxRightY and \
                sMinLeftX < self.vPositionX[15] < sMaxLeftX and \
                sMinLeftY < self.vPositionY[15] < sMaxLeftY:
            self.sCountStill = self.sCountStill + 1
        else:
            self.sCountStill = 0

        self.sRightWristX = self.vPositionX[16]
        self.sRightWristY = self.vPositionY[16]
        self.sLeftWristX = self.vPositionX[15]
        self.sLeftWristY = self.vPositionY[15]

    def isStationary(self):
        if self.sCountStill > self.sFrameStationary:
            return True
        else:
            return False

    def getMarkPosition2D(self):
        return self.vPositionX, self.vPositionY

    def getMarkVisibility(self):
        return self.vVisibility

    def getTiltBody(self):
        vCenterOfShoulder = (
            (self.vPositionX[11] + self.vPositionX[12])/2,
            (self.vPositionY[11] + self.vPositionY[12])/2
        )

        vCenterOfHip = (
            (self.vPositionX[23] + self.vPositionX[24])/2,
            (self.vPositionY[23] + self.vPositionY[24])/2
        )

        return self.getTilt(vCenterOfHip, vCenterOfShoulder)

    def getTiltNeck(self):
        vCenterOfShoulder = (
            (self.vPositionX[11] + self.vPositionX[12])/2,
            (self.vPositionY[11] + self.vPositionY[12])/2
        )

        vNose = (self.vPositionX[0], self.vPositionY[0])

        return self.getTilt(vCenterOfShoulder, vNose)

    def getTiltRightUpperArm(self):
        vRightShoulder = (self.vPositionX[12], self.vPositionY[12])
        vRightElbow = (self.vPositionX[14], self.vPositionY[14])

        return self.getTilt(vRightElbow, vRightShoulder)

    def getTiltRightForearm(self):
        vRightElbow = (self.vPositionX[14], self.vPositionY[14])
        vRightWrist = (self.vPositionX[16], self.vPositionY[16])

        return self.getTilt(vRightWrist, vRightElbow)

    def getTiltLeftUpperArm(self):
        vLeftShoulder = (self.vPositionX[11], self.vPositionY[11])
        vLeftElbow = (self.vPositionX[13], self.vPositionY[13])

        return self.getTilt(vLeftElbow, vLeftShoulder)

    def getTiltLeftForearm(self):
        vLeftElbow = (self.vPositionX[13], self.vPositionY[13])
        vLeftWrist = (self.vPositionX[15], self.vPositionY[15])

        return self.getTilt(vLeftWrist, vLeftElbow)

    def getTilt(self, vPosPivot, vPosPeriphery):
        sDifferenceX = vPosPeriphery[0] - vPosPivot[0]
        sDifferenceY = - (vPosPeriphery[1] - vPosPivot[1])

        if sDifferenceX == 0:
            if sDifferenceY >= 0:
                sTilt = 0
            else:
                sTilt = 180
        elif sDifferenceX >= 0:
            sTilt = 90 - 180 / np.pi * np.arctan(sDifferenceY / sDifferenceX)
        else:
            sTilt = -90 + 180 / np.pi * \
                np.arctan(- sDifferenceY / sDifferenceX)

        return round(sTilt, 2)

    def areArmsCrossed(self):
        sMarginElbow = 50
        sMarginPinky = 25
        if self.vPositionX[13] > self.vPositionX[14] + sMarginElbow and self.vPositionX[18] > self.vPositionX[17] + sMarginPinky:
            return True
        else:
            return False


if __name__ == '__main__':
    import cv2
    import os
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
    cPose.defineROI(sWidth, sRatioROI, "CENTER")

    while True:
        strPose = 'None'
        imInput = cImageSensor.read()
        cPose.searchLandmarks(imInput)
        cPose.drawLandmarks()
        sTiltNeck = cPose.getTiltNeck()
        sTiltBody = cPose.getTiltBody()
        sTiltRightUpperArm = cPose.getTiltRightUpperArm()
        sTiltRightForearm = cPose.getTiltRightForearm()
        sTiltLeftUpperArm = cPose.getTiltLeftUpperArm()
        sTiltLeftForearm = cPose.getTiltLeftForearm()
        blCrossArms = cPose.areArmsCrossed()
        blStill = cPose.isStationary()

        if sTiltLeftForearm > 110 and sTiltRightForearm < -110:
            if blCrossArms:
                strPose = 'Batsu'
            elif sTiltLeftUpperArm < -120 and sTiltRightUpperArm > 120:
                strPose = 'Maru'

        cWindow.setText(0, "Neck : " + str(sTiltNeck), (0, 50))
        cWindow.setText(1, "Body : " + str(sTiltBody), (0, 100))
        cWindow.setText(2, "RUA  : " + str(sTiltRightUpperArm), (0, 150))
        cWindow.setText(3, "RFA  : " + str(sTiltRightForearm), (0, 200))
        cWindow.setText(4, "LUA  : " + str(sTiltLeftUpperArm), (0, 250))
        cWindow.setText(5, "LFA  : " + str(sTiltLeftForearm), (0, 300))
        cWindow.setText(6, "Pose : " + str(strPose), (0, 350))
        cWindow.setText(7, "Still: " + str(blStill), (0, 400))

        for strWindowName in tplWindowNames:
            cWindow.imshow(strWindowName, imInput)

        sKey = cv2.waitKey(1) & 0xFF
        if sKey == ord('q'):
            cPose.finalize()
            cImageSensor.finalize()
            cWindow.finalize()
            break
