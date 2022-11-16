import time
import PySimpleGUI as sg
import pyautogui

from functions.setGUI import setGUI
from functions.common import GetListGames, GetListGameFlags
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
	layoutSelect_Game = make_4choice_layout("images/select.png", GetListGames())
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
	event = dictArgument["Event"]
	cCtrlCard = dictArgument["CtrlCard"]
	cState = dictArgument["State"]
	cLogger = dictArgument["Logger"]
	cAudioOut = dictArgument["AudioOut"]
	blPlayCardEnable = dictArgument["PlayCard"]

	cCtrlCard.initID()

	if blPlayCardEnable:
		if cCtrlCard.readCardInfo() == True:
			if cCtrlCard.readCardRecord() == True:
				dictSaveData = cCtrlCard.getRecord()
				cLogger.logDebug("Save Data:", dictSaveData)

				if dictSaveData["tutorial"] == "T":
					for sGameNumber in range(len(GetListGames())):
						window = cState.dictWindow["SELECT_GAME"]
						if dictSaveData[GetListGameFlags(sGameNumber)] == "T":
							window[GetListGames(sGameNumber)].update(disabled=True)
					cAudioOut.playSoundAsync("sound/card_set_24.wav")
					dictArgument["Start time"] = cState.updateState("SELECT_GAME")
				else:
					cLogger.logDebug("Tutorial flag is not found")
					cAudioOut.playSoundAsync("sound/card_set_24.wav", "sound/title_24.wav")
					dictArgument["Start time"] = cState.updateState("TITLE")				
			else:
				cLogger.logDebug("Blank card is placed")
				cCtrlCard.initRecord()
				cAudioOut.playSoundAsync("sound/card_set_24.wav", "sound/title_24.wav")
				dictArgument["Start time"] = cState.updateState("TITLE")
	else:
		if cCtrlCard.readCardInfo() == True:
			pass
		elif event == "STANDBY":
			for sNumOfGame in range(4):
				window = cState.dictWindow["SELECT_GAME"]
				window[GetListGames(sNumOfGame)].update(disabled=False)
			cAudioOut.playSoundAsync("sound/title_24.wav")
			dictArgument["Start time"] = cState.updateState("TITLE")


# TITLEモード処理 ======================================================
def titleModeProc(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]

	if event == "TITLE" and cAudioOut.getSoundEnd() == True:
		cAudioOut.playSoundAsync("sound/tutorial1_24.wav")
		dictArgument["Start time"] = cState.updateState("TUTORIAL_1")
		#dictArgument["Start time"] = cState.updateState("SELECT_GAME")


# SELECT_GAMEモード処理 =================================================
def select_game_ModeProc(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]

	if event == GetListGames(0):
		cAudioOut.enableStateChange("SPEECH_Q2")
		cAudioOut.playSoundAsync("sound/speech_24.wav")
		dictArgument["Start time"] = cState.updateState("SPEECH_Q1")
	elif event == GetListGames(1):
		dictArgument["Start time"] = cState.updateState("POSE_Q")
	elif event == GetListGames(2):
		dictArgument["Start time"] = cState.updateState("QR_Q")
	elif event == GetListGames(3):
		sStartTime = cState.updateState("SELECT_Q1")
		cAudioOut.playSoundAsync("sound/oit_24.wav")
		dictArgument["Start time"] = sStartTime


# ENDINGモード処理 =========================================================
def endingModeProc(dictArgument):
	pass


# card_errorモード処理 ======================================================
def card_error_ModeProc(dictArgument):
	cState = dictArgument["State"]
	sTimeout = 3

	if time.time() - dictArgument["Start time"] > sTimeout:
		dictArgument["Start time"] = cState.updateState("STANDBY")
