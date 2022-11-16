# ライブラリ等のインポート ==============================================
import pyautogui
import yaml
import os

from functions.ModeFuncBase import *
from functions.ModeFuncTutorial import *
from functions.ModeFuncSpeech import *
from functions.ModeFuncPose import *
from functions.ModeFuncSelect import *
from functions.ModeFuncQR import *
from functions.common import GetDictFlag, CheckCard

from Classes.ClsCtrlStateAndWindow import ClsCtrlStateAndWindow
from Classes.ClsLogger import ClsLogger
from Classes.ClsAudioIn import ClsAudioIn
from Classes.ClsAudioOut import ClsAudioOut
from Classes.ClsImageSensor import ClsImageSensor
from Classes.ClsWindow import ClsWindow
from Classes.ClsPoseEstimation import ClsPoseEstimation
from Classes.ClsImageProcessQR import ClsImageProcessQR
from Classes.ClsImageProcessGlico import ClsImageProcessGlico

if os.name == 'nt':
    from Classes.ClsNtagIFDummy import ClsNtagIF
else:
    from Classes.ClsNtagIF import ClsNtagIF
    from functions.AdminMode import AdminModeIndependent

import sys
sys.path.append("./Classes")


# 画像IF設定 =========================================================
def prepareImageIF(cLogger):
    if os.name == 'nt':
        strPlatform = "WIN"
    else:
        strPlatform = "JETSON"

    sCameraNumber = 0
    sSensorWidth = 320
    sSensorHeight = 180
    sMonitorWidth = 1024
    sMonitorHeight = 600
    tplWindowName = ("full",)
    blSensorFlip = False
    blMonitorFlip = True

    sRatioROI = 0.6

    cImageSensor = ClsImageSensor(
        strPlatform, sCameraNumber, sSensorWidth, sSensorHeight, blSensorFlip,
    )
    sWidthInput, sHeightInput = cImageSensor.getImageSize()

    cWindow = ClsWindow(tplWindowName, blMonitorFlip)
    cWindow.prepareFullScreen(
        sMonitorWidth, sMonitorHeight, sWidthInput, sHeightInput
    )

    cPose = ClsPoseEstimation(0.5, 0.5)
    cPose.defineROI(sWidthInput, sRatioROI, "CENTER")

    cImageProcGlico = ClsImageProcessGlico(cLogger, cImageSensor, cWindow)
    cImageProcGlico.setPoseClass(cPose)
    cImageProcQR = ClsImageProcessQR(cLogger, cImageSensor, cWindow)
    cImageProcQR.setAnswer("LenaKnows")
    listImageProc = [cImageProcGlico, cImageProcQR]

    return listImageProc, cImageSensor, cWindow, cPose


# 音声IF設定 =========================================================
def prepareAudioIF(cLogger):
    sChannels = 1
    sRate = 22050
    sUnitSample = 1024
    cAudioIn = ClsAudioIn(cLogger, sChannels, sRate, sUnitSample)
    cAudioOut = ClsAudioOut(cLogger)

    return cAudioIn, cAudioOut


# モード別設定 =============================================================
def setModeFuncsAndLayouts(blDebug):
    dictWindow = createDictWindow()
    dictWindow = updateDictWindow_Tutorial(dictWindow)
    dictWindow = updateDictWindow_Speech(dictWindow)
    dictWindow = updateDictWindow_Pose(dictWindow)
    dictWindow = updateDictWindow_Select(dictWindow)
    dictWindow = updateDictWindow_QR(dictWindow)

    if blDebug == False:
        for sKey in dictWindow:
            window = dictWindow[sKey]
            if window != "None":
                window.set_cursor("none")

    cState = ClsCtrlStateAndWindow("STANDBY", "BACKGROUND", dictWindow)

    dictProc = createDictProc()
    dictProc = updateDictProc_Tutorial(dictProc)
    dictProc = updateDictProc_Speech(dictProc)
    dictProc = updateDictProc_Pose(dictProc)
    dictProc = updateDictProc_Select(dictProc)
    dictProc = updateDictProc_QR(dictProc)

    dictFlag = GetDictFlag()

    return cState, dictProc, dictFlag


# メインスレッド =======================================================
def mainThread():
    blDebug = True
    blPlayCardEnable = True
    cLogger = ClsLogger("tOITe")
    listImageProc, cImageSensor, cWindow, cPose = prepareImageIF(cLogger)
    cAudioIn, cAudioOut = prepareAudioIF(cLogger)
    cState, dictProc, dictFlag = setModeFuncsAndLayouts(blDebug)
    cState.setLogger(cLogger)
    cCtrlCard = ClsNtagIF(cLogger, dictFlag, blPlayCardEnable)

    with open("files/Admin_CardID_list.yaml", "r") as f:
        listAdminCardID = yaml.safe_load(f)["card_ID"]

    dictArgument = {
        "State": cState,
        "CtrlCard": cCtrlCard,
        "Logger": cLogger,
        "PlayCard": blPlayCardEnable,
        "ListImageProc": listImageProc,
        "AudioIn": cAudioIn,
        "AudioOut": cAudioOut,
        "Event": None,
        "Values": None,
        "Return state": None,  # カードエラーからの復帰位置
        "Frame": 0,
        "Start time": 0,
        "Option": [0, 0, 0, 0, 0, 0, 0, 0],
        "Complete": 0,
    }

    cAudioOut.setDictArgument(dictArgument)
    cAudioOut.setClsCtrlState(cState)

    # 無限ループ ----------------------------------------
    while True:
        if dictArgument["Complete"] == 1:
            break

        if blDebug == False:
            pyautogui.moveTo(2, 2)

        # フレームを記録
        dictArgument["Frame"] = (dictArgument["Frame"] + 1) % 1000

        # 現在のステートを確認
        currentState = cState.getState()

        if cState.dictWindow[currentState] != "None":
            # ウィンドウからイベントを受信
            event, values = cState.readEvent()
            dictArgument["Event"] = event
            dictArgument["Values"] = values

            if event != "-timeout-":
                cLogger.logDebug("Event : ", event)

        if currentState != "CARD_ERROR" and currentState != "STANDBY":
            currentState = CheckCard(dictArgument)  # カードの存在をチェック

        strCardID = cCtrlCard.getID()
        if strCardID in listAdminCardID:
            cLogger.logDebug("Admin card was placed")
            break

        dictProc[currentState](dictArgument)

    cAudioIn.finalize()
    # cAudioOut.finalize()
    for sNumOfProc in range(len(listImageProc)):
        cProc = listImageProc[sNumOfProc]
        cProc.finalize()
    cPose.finalize()
    cImageSensor.finalize()
    cWindow.finalize()
    cCtrlCard.finalize()
    cState.finalize()

    cLogger.logDebug("Finished finalize procedures")
    cLogger.finalize()

    return strCardID


# メイン関数 =================================================
if __name__ == "__main__":
    while True:
        strCardID = mainThread()

        if os.name == 'nt':
            adminCommand = "end"
        else:
            adminCommand = AdminModeIndependent()

        if adminCommand == "end":
            break
