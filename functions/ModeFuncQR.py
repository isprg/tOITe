import cv2
from functions.common import GetListGames, GetListGameFlags
from functions.setGUI import setGUI
from functions.DesignLayout import make_fullimage_layout


# 処理の辞書割り当て ======================================================
def updateDictProc_QR(dictProc):
    dictProc_this = {
        "QR_Q": procQR_Q,
        "QR_IMGPROC": procQR_ImageProc,
        "QR_CORRECT": procQR_correct,
    }
    return dict(dictProc, **dictProc_this)


# レイアウト設定・辞書割り当て =============================================
def updateDictWindow_QR(dictWindow):
    layoutQR_Q = make_fullimage_layout("images/qr.png", "QR_Q")
    layoutQR_Correct = make_fullimage_layout(
        "images/correct.png", "QR_CORRECT")

    dictLayout = {
        "QR_Q": layoutQR_Q,
        "QR_IMGPROC": "None",
        "QR_CORRECT": layoutQR_Correct
    }
    dictWindow_this = setGUI(dictLayout)

    return dict(dictWindow, **dictWindow_this)


# QR_Qモード処理 ==============================================
def procQR_Q(dictArgument):
    event = dictArgument["Event"]
    cState = dictArgument["State"]
    cProc = dictArgument["ListImageProc"][1]
    cAudioOut = dictArgument["AudioOut"]

    if event == "QR_Q":
        dictArgument["Start time"] = cState.updateState("QR_IMGPROC")
        cProc.clearWindowText()
        cProc.createWindows()


# QR_IMGPROCモード処理 ======================================================
def procQR_ImageProc(dictArgument):
    cState = dictArgument["State"]
    sFrame = dictArgument["Frame"]
    cProc = dictArgument["ListImageProc"][1]
    cCtrlCard = dictArgument["CtrlCard"]
    cAudioOut = dictArgument["AudioOut"]
    cLogger = dictArgument["Logger"]

    isFound = cProc.execute()
    cv2.waitKey(1)

    if isFound == True:
        cLogger.logDebug("QR code is correct")
    elif isFound == False and sFrame % 60 == 0:
        cLogger.logDebug("Frame :", sFrame, ", QR code is not found")

    if isFound is True:
        cAudioOut.playSoundAsync("sound/correct_24.wav")
        dictArgument["Start time"] = cState.updateState("QR_CORRECT")
        cProc.closeWindows()
        cCtrlCard.writeCardRecord(GetListGameFlags(2), "T")
        cState.dictWindow["SELECT_GAME"][GetListGames(2)].update(disabled=True)


# POSE_CORRECTモード処理　======================================================
def procQR_correct(dictArgument):
    event = dictArgument["Event"]
    cState = dictArgument["State"]

    if event == "QR_CORRECT":
        dictArgument["Start time"] = cState.updateState("SELECT_GAME")
