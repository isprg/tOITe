import time
import PySimpleGUI as sg
import pyautogui

from functions.setGUI import setGUI
from functions.common import Reset_Game, CheckTappedArea
from functions.DesignLayout import *


# 処理の辞書割り当て ======================================================
def createDictProc():
	dictProc = {
		"STANDBY"			: standbyModeProc,
		"TITLE"				: titleModeProc,
		"SELECT_GAME"		: select_game_ModeProc,
		"ENDING"			: endingModeProc,
		"CARD_ERROR"		: card_error_ModeProc,
	}
	return dictProc


# レイアウト設定・辞書割り当て =============================================
def createDictWindow():
	layoutBackGround = [[sg.Text()]]
	layoutStandby = make_fullimage_layout("images/standby.png", "STANDBY")
	layoutTitle = make_fullimage_layout("images/title.png", "TITLE")
	layoutSelect_Game = make_4choice_layout("images/select.png", ["音声認識", "姿勢推定", "多岐選択", ""])
	layoutEnding = make_fullimage_layout("images/ending.png", "ENDING")
	layoutCard_Error = make_fullimage_layout("images/card_alert.png", "CARD_ERROR")

	dictLayout = {
		"BACKGROUND"  : layoutBackGround,
		"STANDBY"     : layoutStandby,
		"TITLE"       : layoutTitle,
		"SELECT_GAME" : layoutSelect_Game,
		"ENDING"      : layoutEnding,
		"CARD_ERROR"  : layoutCard_Error,
    }
	dictWindow = setGUI(dictLayout)
	
	return dictWindow


# STANDBYモード処理 ======================================================
def standbyModeProc(dictArgument):
	cCtrlCard = dictArgument["CtrlCard"]
	cState = dictArgument["State"]
	cLogger = dictArgument["Logger"]
	cAudioOut = dictArgument["AudioOut"]

	cCtrlCard.initID()
	setFlag = cCtrlCard.setCard()

	if setFlag:
		dictSaveData = cCtrlCard.read_result()
		cLogger.logDebug("Save Data:", dictSaveData)

		if dictSaveData["tutorial"] == "T":
			if dictSaveData["speech"] == "T":
				cState.dictWindow["SELECT_GAME"]["音声認識"].update(disabled=True)
			if dictSaveData["pose"] == "T":
				cState.dictWindow["SELECT_GAME"]["姿勢推定"].update(disabled=True)
			if dictSaveData["select"] == "T":
				cState.dictWindow["SELECT_GAME"]["多岐選択"].update(disabled=True)
			
			cAudioOut.playSoundAsync("sound/card_set_24.wav")
			dictArgument["Start time"] = cState.updateState("SELECT_GAME")

		else:
			cLogger.logDebug("Blank card was placed")
			cCtrlCard.initCard()
			cAudioOut.playSoundAsync("sound/card_set_24.wav", "sound/title_24.wav")
			dictArgument["Start time"] = cState.updateState("TITLE")


# TITLEモード処理 ======================================================
def titleModeProc(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]

	if event == "TITLE" and cAudioOut.getSoundEnd() == True:
		cAudioOut.playSoundAsync("sound/tutorial1_24.wav")
		dictArgument["Start time"] = cState.updateState("TUTORIAL_1")


# SELECT_GAMEモード処理 =================================================
def select_game_ModeProc(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	proc = dictArgument["ImageProc"]
	cCtrlCard = dictArgument["CtrlCard"]
	cAudioOut = dictArgument["AudioOut"]

	if event == "音声認識":
		cAudioOut.enableStateChange("SPEECH_Q2")
		cAudioOut.playSoundAsync("sound/speech_24.wav")
		dictArgument["Start time"] = cState.updateState("SPEECH_Q1")
	elif event == "姿勢推定":
		dictArgument["Start time"] = cState.updateState("POSE_Q")
	elif event == "多岐選択":
		sStartTime = cState.updateState("SELECT_Q1")
		cAudioOut.playSoundAsync("sound/oit_24.wav")
		dictArgument["Start time"] = sStartTime
#	elif event == "画像":
#		sStartTime = cState.updateState("QR_Q")
#		proc.createWindows()
#		dictArgument["Start time"] = sStartTime


# ENDINGモード処理 =========================================================
def endingModeProc(dictArgument):
	event = dictArgument["Event"]
	
	if event == "ENDING":
		dictArgument["Complete"] = 1


# card_errorモード処理 ======================================================
def card_error_ModeProc(dictArgument):
	cState = dictArgument["State"]
	cCtrlCard = dictArgument["CtrlCard"]
	proc = dictArgument["ImageProc"]

	exist = cCtrlCard.check_exist()  # カードが存在するかをチェック
	identical = cCtrlCard.check_identity()  # カードが同一かをチェック
	if exist is True and identical is True:
		ReturnState, ImageProc_Flag = dictArgument["Return state"]

		if ImageProc_Flag:
			proc.createWindows()

		dictArgument["Start time"] = cState.updateState(ReturnState)
		dictArgument["Return state"] = None

	elif identical is False or time.time() - dictArgument["Start time"] > 5:
		Reset_Game(dictArgument)