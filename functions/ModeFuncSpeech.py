import pyautogui
import speech_recognition as sr
from functions.setGUI import setGUI
from functions.common import CheckTappedArea
from functions.DesignLayout import make_fullimage_layout


def updateDictProc_Speech(dictProc):
	dictProc_this = {
		"SPEECH_Q1"     : procSpeech_Q1,
		"SPEECH_Q2"     : procSpeech_Q2,
		"SPEECH_CORRECT": procSpeech_Correct,
		"SPEECH_WRONG"  : procSpeech_Wrong,
	}
	return dict(dictProc, **dictProc_this)


def updateDictWindow_Speech(dictWindow):
	layoutSpeech_Q1 = make_fullimage_layout("images/speech1.png", "SPEECH_Q1")
	layoutSpeech_Q2 = make_fullimage_layout("images/speech2.png", "SPEECH_Q2")
	layoutSpeech_Correct = make_fullimage_layout(
		"images/correct.png", "SPEECH_CORRECT")
	layoutSpeech_Wrong = make_fullimage_layout("images/wrong.png", "SPEECH_WRONG")

	dictLayout = {
		"SPEECH_Q1"		: layoutSpeech_Q1,
		"SPEECH_Q2"		: layoutSpeech_Q2,
		"SPEECH_CORRECT": layoutSpeech_Correct,
		"SPEECH_WRONG"	: layoutSpeech_Wrong,
	}
	dictWindow_this = setGUI(dictLayout)

	return dict(dictWindow, **dictWindow_this)


# 標準タップ座標設定 ================================================
def getAreaDefinition():
	vArea0 = [20, 500, 480, 70]
	vArea1 = [520, 500, 480, 70]
	listArea = [vArea0, vArea1, ]

	return listArea


# 音声テキスト変換　=========================================================
def convAudioToText(strAudioFileName):
	recog = sr.Recognizer()
	try:
		with sr.AudioFile(strAudioFileName) as inputAudio:
			audio = recog.record(inputAudio)
		strVoice = recog.recognize_google(audio, language='ja-JP')
	except sr.UnknownValueError:
		return "UnknownValueError"
	except sr.RequestError:
		return "RequestError"
	
	return strVoice


# キーワード判定　===========================================================
def judgeKeyword(strKeyword, strVoice):
	if strKeyword in strVoice:
		return True
	else:
		return False


# SPEECH_Q1モード処理　======================================================
def procSpeech_Q1(dictArgument):
	pass


# SPEECH_Q2モード処理　======================================================
def procSpeech_Q2(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cLogger = dictArgument["Logger"]
	cAudioIn = dictArgument["AudioIn"]
	cAudioOut = dictArgument["AudioOut"]
	strVoiceFileName = "voice.wav"

	if event == "SPEECH_Q2":
		vPosition = pyautogui.position()
		listArea = getAreaDefinition()
		sTappedArea = CheckTappedArea(vPosition, listArea)

		if sTappedArea == 0 and cAudioIn.getRecording() == False and cAudioOut.getSoundEnd() == True:
			cLogger.logDebug("start recording")
			cAudioOut.playSoundAsync("sound/button1_44.wav")
			cAudioIn.startRecordThread()
		elif sTappedArea == 1 and cAudioIn.getRecording() == True and cAudioOut.getSoundEnd() == True:
			cLogger.logDebug("stop recording")
			cAudioOut.playSoundAsync("sound/button1_44.wav")
			cAudioIn.setRecording(False)
			cAudioIn.record(strVoiceFileName)
			strVoice = convAudioToText(strVoiceFileName)
			cLogger.logDebug(strVoice)

			listCorrect = [False, False, False]

			if judgeKeyword("大正", strVoice):
				listCorrect[0] = True
			if judgeKeyword("昭和", strVoice):
				listCorrect[1] = True
			if judgeKeyword("平成", strVoice):
				listCorrect[2] = True

			if listCorrect == [True, True, True]:
				cAudioOut.playSoundAsync("sound/correct_24.wav")
				dictArgument["Start time"] = cState.updateState("SPEECH_CORRECT")
			else:
				cAudioOut.playSoundAsync("sound/wrong_24.wav")
				dictArgument["Start time"] = cState.updateState("SPEECH_WRONG")


# SPEECH_CORRECTモード処理　==================================================
def procSpeech_Correct(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cCtrlCard = dictArgument["CtrlCard"]

	if event == "SPEECH_CORRECT":
		cCtrlCard.write_result("speech", "T")
		dictArgument["Start time"] = cState.updateState("SELECT_GAME")
		cState.dictWindow["SELECT_GAME"]["音声認識"].update(disabled=True)


# SPEECH_WRONGモード処理　===================================================
def procSpeech_Wrong(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cCtrlCard = dictArgument["CtrlCard"]

	if event == "SPEECH_WRONG":
		dictArgument["Start time"] = cState.updateState("SPEECH_Q2")
