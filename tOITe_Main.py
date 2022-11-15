# ライブラリ等のインポート ==============================================
import pyautogui
import yaml
import os

from functions.ModeFuncBase import *
from functions.ModeFuncTutorial import *
from functions.ModeFuncSpeech import *
from functions.ModeFuncPose import *
from functions.ModeFuncSelect import *
from functions.CardFunc import *
from functions.common import getDictFlag
from Classes.ClsCtrlStateAndWindow import ClsCtrlStateAndWindow
from Classes.ClsLogger import ClsLogger

if os.name == 'nt':
	from Classes.ClsCtrlCardDummy import ClsCtrlCard
else:
	from Classes.ClsCtrlCard import ClsCtrlCard
	from functions.AdminMode import AdminMode

import sys
sys.path.append("./Classes")
from ClsImageProcessPose import ClsImageProcessPose
from ClsAudioIn import ClsAudioIn
from ClsAudioOut import ClsAudioOut


# 環境設定 =============================================================
def setEnvironment():
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
	sFlipMode = 2

	cImageProc = ClsImageProcessPose(
		strPlatform,
		sCameraNumber,
		sSensorWidth,
		sSensorHeight,
		sMonitorWidth,
		sMonitorHeight,
		tplWindowName,
		sFlipMode,
	)

	cLogger = ClsLogger()

	sChannels = 1
	sRate = 22050
	sUnitSample = 1024
	cAudioIn = ClsAudioIn(cLogger, sChannels, sRate, sUnitSample)
	cAudioOut = ClsAudioOut(cLogger)

	return cLogger, cImageProc, cAudioIn, cAudioOut


# モード別設定 =============================================================
def setModeFuncsAndLayouts(blDebug):
	dictWindow = createDictWindow()
	dictWindow = updateDictWindow_Tutorial(dictWindow)
	dictWindow = updateDictWindow_Speech(dictWindow)
	dictWindow = updateDictWindow_Pose(dictWindow)
	dictWindow = updateDictWindow_Select(dictWindow)

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

	dictFlag = getDictFlag()

	return cState, dictProc, dictFlag


# メインスレッド =======================================================
def mainThread():
	blDebug = True
	cLogger, cImageProc, cAudioIn, cAudioOut = setEnvironment()
	cState, dictProc, dictFlag = setModeFuncsAndLayouts(blDebug)
	cState.setLogger(cLogger)
	cCtrlCard = ClsCtrlCard(dictFlag)

	listFlags = list(dictFlag.keys())
	cLogger.logDebug(listFlags[0])
	
	# 管理者カードの一覧を取得
	with open("files/Admin_CardID_list.yaml", "r") as f:
		listAdminCardID = yaml.safe_load(f)["card_ID"]

	dictArgument = {
		"State"			: cState,
		"CtrlCard"		: cCtrlCard,
		"Logger"		: cLogger,
		"ImageProc"		: cImageProc,
		"AudioIn"		: cAudioIn,
		"AudioOut"		: cAudioOut,
		"Event"			: None,
		"Values"		: None,
		"Return state"	: None,  # カードエラーからの復帰位置
		"Frame"			: 0,
		"Start time"	: 0,
		"Option"		: [0,0,0,0,0,0,0,0],
		"Complete"		: 0,
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
			# カードの状態をチェック
			currentState = CheckCard(dictArgument)  # カードの存在と同一性をチェック

			strCardID = cCtrlCard.getID()
			if strCardID in listAdminCardID:
				cLogger.logDebug("Admin card was placed")
				break

		dictProc[currentState](dictArgument)

	cAudioIn.finalize()
	#cAudioOut.finalize()
	cImageProc.Finalize()
	cCtrlCard.Finalize()
	cState.Finalize()

	cLogger.logDebug("Finished finalize procedures")

	return strCardID


# メイン関数 =================================================
if __name__ == "__main__":
	while True:
		strCardID = mainThread()

		if os.name == 'nt':
			adminCommand = "end"
		else:
			adminCommand = AdminMode(strCardID)

		if adminCommand == "end":
			break
