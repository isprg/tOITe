import pyautogui
from functions.setGUI import setGUI
from functions.common import CheckTappedArea
from functions.DesignLayout import make_fullimage_layout


# 処理の辞書割り当て ======================================================
def updateDictProc_Select(dictProc):
	dictProc_this = {
		"SELECT_Q1": procSelect_Q1,
		"SELECT_Q2": procSelect_Q2,
	}
	return dict(dictProc, **dictProc_this)


# レイアウト設定・辞書割り当て =============================================
def updateDictWindow_Select(dictWindow):
	layoutSelectQ1 = make_fullimage_layout("images/oit1.png", "SELECT_Q1")
	layoutSelectQ2 = make_fullimage_layout("images/oit2.png", "SELECT_Q2")

	dictLayout = {
		"SELECT_Q1": layoutSelectQ1,
		"SELECT_Q2": layoutSelectQ2,
	}
	dictWindow_this = setGUI(dictLayout)

	return dict(dictWindow, **dictWindow_this)


# 標準タップ座標設定 ================================================
def getAreaDefinition():
	vArea0 = [50, 55, 430, 250]
	vArea1 = [545, 55, 430, 250]
	vArea2 = [50, 315, 430, 250]
	vArea3 = [545, 315, 430, 250]

	listArea = [vArea0, vArea1, vArea2, vArea3]

	return listArea


# Select_1モード処理 ==============================================
def procSelect_Q1(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cAudioOut = dictArgument["AudioOut"]

	if event == "SELECT_Q1" and cAudioOut.getSoundEnd() == True:
		dictArgument["Start time"] = cState.updateState("SELECT_Q2")
		dictArgument["Option"] = [0,0,0,0,0,0,0,0]


# SELECT_2モード処理 ==============================================
def procSelect_Q2(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	cLogger = dictArgument["Logger"]
	cAudioOut = dictArgument["AudioOut"]
	vHistory = dictArgument["Option"]

	if event == "SELECT_Q2":
		vPosition = pyautogui.position()
		listArea = getAreaDefinition()
		sTappedArea = CheckTappedArea(vPosition, listArea)

		if sTappedArea == 1:
			cAudioOut.playSoundAsync("sound/correct_24.wav")
			vHistory[0] = 1
		elif sTappedArea == 2:
			cAudioOut.playSoundAsync("sound/correct_24.wav")
			vHistory[1] = 1
		else:
			cAudioOut.playSoundAsync("sound/wrong_24.wav")
		
		cLogger.logDebug("Option : ", dictArgument["Option"])

		if vHistory[0:2] == [1,1]:
			dictArgument["Start time"] = cState.updateState("SELECT_GAME")
			cState.dictWindow["SELECT_GAME"]["多岐選択"].update(disabled=True)
			vHistory[0:2] = [0,0]
	



