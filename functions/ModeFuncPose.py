import cv2
from functions.common import GetListGames, GetListGameFlags
from functions.setGUI import setGUI
from functions.DesignLayout import make_fullimage_layout


# 処理の辞書割り当て ======================================================
def updateDictProc_Pose(dictProc):
	dictProc_this = {
		"POSE_Q"			: procPose_Q,
		"POSE_IMGPROC"		: procPose_ImageProc,
		"POSE_CORRECT"      : procPose_correct,
	}
	return dict(dictProc, **dictProc_this)


# レイアウト設定・辞書割り当て =============================================
def updateDictWindow_Pose(dictWindow):
	layoutPose_Q = make_fullimage_layout("images/glico.png", "POSE_Q")
	layoutPose_Correct = make_fullimage_layout("images/correct.png", "POSE_CORRECT")

	dictLayout = {
		"POSE_Q"			: layoutPose_Q,
		"POSE_IMGPROC"		: "None",
		"POSE_CORRECT"      : layoutPose_Correct
	}
	dictWindow_this = setGUI(dictLayout)

	return dict(dictWindow, **dictWindow_this)


# POSE_Qモード処理 ==============================================
def procPose_Q(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	proc = dictArgument["ListImageProc"][0]
	cAudioOut = dictArgument["AudioOut"]

	if event == "POSE_Q":
		dictArgument["Start time"] = cState.updateState("POSE_IMGPROC")
		proc.createWindows()


# POSE_IMGPROCモード処理 ======================================================
def procPose_ImageProc(dictArgument):
	cState = dictArgument["State"]
	sFrame = dictArgument["Frame"]
	cProc = dictArgument["ListImageProc"][0]
	cCtrlCard = dictArgument["CtrlCard"]
	cAudioOut = dictArgument["AudioOut"]
	cLogger = dictArgument["Logger"]

	isFound = cProc.execute()
	cv2.waitKey(1)

	if isFound == True:
		cLogger.logDebug("The pose is correct")
	elif isFound == False and sFrame % 60 == 0:
		cLogger.logDebug("Frame :",sFrame, ", The pose is not found")

	if isFound is True:
		cAudioOut.playSoundAsync("sound/correct_24.wav")
		dictArgument["Start time"] = cState.updateState("POSE_CORRECT")
		cProc.closeWindows()
		cCtrlCard.writeCardRecord(GetListGameFlags(1), "T")
		cState.dictWindow["SELECT_GAME"][GetListGames(1)].update(disabled=True)


# POSE_CORRECTモード処理　======================================================
def procPose_correct(dictArgument):
	event = dictArgument["Event"]
	cState = dictArgument["State"]
	
	if event == "POSE_CORRECT":
		dictArgument["Start time"] = cState.updateState("SELECT_GAME")

