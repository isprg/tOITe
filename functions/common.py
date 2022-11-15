import csv
import os
import subprocess


# アンケート結果をCSVファイルに保存
def getDictFlag():
	dictFlag = {
		"tutorial"		: "チュートリアル",
		"speech"		: "音声認識",
		"pose"			: "姿勢推定",
		"select"		: "多岐選択",
		"complete"		: "クリア",
	}

	return dictFlag

	
# アンケート結果をCSVファイルに保存
def Record_to_CSV(dictArgument):
	cCtrlCard = dictArgument["CtrlCard"]
	dictSaveData = cCtrlCard.read_result()
	Card_ID = cCtrlCard.getID()

	listSurveyResult = [dictSaveData["survey" + str(i + 1)] for i in range(5)]
	listSurveyResult.insert(0, Card_ID)
	with open("files/survey_result.csv", "a") as f:
		writer = csv.writer(f)
		writer.writerow(listSurveyResult)

	cCtrlCard.write_result("finish_survey", "T")  # アンケート回答済みであることを記録


# ゲームを初期化
def Reset_Game(dictArgument):
	sStartTime = dictArgument["State"].updateState("STANDBY")
	dictArgument["ImageProc"].reset()
	dictArgument["Event"] = None
	dictArgument["Values"] = None
	dictArgument["Frame"] = 0
	dictArgument["Start time"] = sStartTime


# ゲームをクリアしたかを判定
def CheckComplete(cCtrlCard, dictFlag):
	dictSaveData = cCtrlCard.read_result()

	bClear = True
	for key in dictFlag.keys():
		if dictSaveData[key] != "T" and key != "complete":
			bClear = False
			break

	return bClear


def PlaySound(path):
	if os.name != 'nt':
		subprocess.Popen(["aplay", "--quiet", path])
	print('play sound')


def CheckTappedArea(vPosition, listArea):
	sTappedArea = -1
	for sAreaNumber in range(len(listArea)):
		sMinX = listArea[sAreaNumber][0]
		sMaxX = listArea[sAreaNumber][0] + listArea[sAreaNumber][2]
		sMinY = listArea[sAreaNumber][1]
		sMaxY = listArea[sAreaNumber][1] + listArea[sAreaNumber][3]

		if(vPosition.x > sMinX and vPosition.x < sMaxX 
		and vPosition.y > sMinY and vPosition.y < sMaxY):
			sTappedArea = sAreaNumber
			break

	return sTappedArea
			