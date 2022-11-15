import pyautogui
from functions.setGUI import setGUI
from functions.common import CheckTappedArea
from functions.DesignLayout import make_fullimage_layout


# 処理の辞書割り当て ======================================================
def updateDictProc_Tutorial(dictProc):
	dictProc_this = {
		"TUTORIAL_1": procTutorial_1,
		"TUTORIAL_2": procTutorial_2,
		"TUTORIAL_3": procTutorial_3,
	}
	return dict(dictProc, **dictProc_this)


# レイアウト設定・辞書割り当て =============================================
def updateDictWindow_Tutorial(dictWindow):
	layoutTutorial1 = make_fullimage_layout("images/tutorial1.png", "TUTORIAL_1")
	layoutTutorial2 = make_fullimage_layout("images/tutorial2.png", "TUTORIAL_2")
	layoutTutorial3 = make_fullimage_layout("images/tutorial3.png", "TUTORIAL_3")

	dictLayout = {
		"TUTORIAL_1": layoutTutorial1,
		"TUTORIAL_2": layoutTutorial2,
		"TUTORIAL_3": layoutTutorial3,
	}
	dictWindow_this = setGUI(dictLayout)

	return dict(dictWindow, **dictWindow_this)


# 標準タップ座標設定 ================================================
def getDefaultAreaDefinition():
	vArea0 = [260, 520, 520, 60]
	listArea = [vArea0, ]

	return listArea


# TUTORIAL_1モード処理 ==============================================
def procTutorial_1(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]

	if event == "TUTORIAL_1" and cAudioOut.getSoundEnd() == True:
		cAudioOut.playSoundAsync("sound/tutorial2_24.wav")
		dictArgument["Start time"] = cState.updateState("TUTORIAL_2")


# TUTORIAL_2モード処理 ==============================================
def procTutorial_2(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]

	if event == "TUTORIAL_2" and cAudioOut.getSoundEnd() == True:
		cAudioOut.playSoundAsync("sound/tutorial3_24.wav")
		dictArgument["Start time"] = cState.updateState("TUTORIAL_3")


# TUTORIAL_3モード処理 ==============================================
def procTutorial_3(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]
	cCtrlCard = dictArgument["CtrlCard"]

	if event == "TUTORIAL_3" and cAudioOut.getSoundEnd() == True:
		cCtrlCard.write_result("tutorial", "T")
		dictArgument["Start time"] = cState.updateState("SELECT_GAME")

