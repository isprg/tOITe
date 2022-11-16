import csv


def GetListGames(sNumOfGame=None):
	listGames = ["音声認識", "姿勢推定", "QRコード", "多岐選択"]
	if sNumOfGame == None:
		return listGames
	else:
		return listGames[sNumOfGame]

def GetListGameFlags(sNumOfGame=None):
	listGameFlags = ["speech", "pose", "qr", "select"]
	if sNumOfGame == None:
		return listGameFlags
	else:
		return listGameFlags[sNumOfGame]

def GetDictFlag():
	dictFlag = {
		"tutorial"			: "チュートリアル",
		GetListGameFlags(0)	: GetListGames(0),
		GetListGameFlags(1)	: GetListGames(1),
		GetListGameFlags(2)	: GetListGames(2),
		GetListGameFlags(3)	: GetListGames(3),
	}
	return dictFlag

# カードの状態をチェック
def CheckCard(dictArgument):
	cLogger = dictArgument["Logger"]
	cState = dictArgument["State"]
	cCtrlCard = dictArgument["CtrlCard"]
	cProc = dictArgument["ListImageProc"][0]
	blPlayCard = dictArgument["PlayCard"]

	# カードが存在するかをチェック
	if blPlayCard:
		if cCtrlCard.readCardInfo() == False:
			cLogger.logDebug("Card Error")
			if cState.dictWindow[cState.strState] == "None":
				cProc.closeWindows()

			dictArgument["Return state"] = (cState.strState, True)
			dictArgument["Start time"] = cState.updateState("CARD_ERROR")

			return "CARD_ERROR"
		else:
			return cState.strState
	else:
		cCtrlCard.readCardInfo()
		return cState.strState
		


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


def Record_to_CSV(dictArgument):
	cCtrlCard = dictArgument["CtrlCard"]

	cCtrlCard.readCardRecord()
	dictSaveData = cCtrlCard.getRecord()
	strCardID = cCtrlCard.getID()

	listSurveyResult = [dictSaveData["survey" + str(i + 1)] for i in range(5)]
	listSurveyResult.insert(0, strCardID)
	with open("files/survey_result.csv", "a") as f:
		writer = csv.writer(f)
		writer.writerow(listSurveyResult)

	cCtrlCard.writeCardRecord("finish_survey", "T")  # アンケート回答済みであることを記録



			
