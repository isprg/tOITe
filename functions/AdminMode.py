from tty import CC
import yaml

from Classes.ClsNtagIF import ClsNtagIF
from Classes.ClsLogger import ClsLogger
from functions.common import GetDictFlag
from functions.AdminModeWindow import *


# Adminカード登録 =============================================
def Register_Admin_Card(cLogger):
	dictFlag = GetDictFlag()
	cCtrlCard = ClsNtagIF(cLogger, dictFlag, False)

	strFilePath = "files/Admin_CardID_list.yaml"
	with open(strFilePath, "r") as f:
		listCardID = yaml.safe_load(f)["card_ID"]

	strIdList = ""
	for i in listCardID:
		strIdList += i
		strIdList += "\n"

	window = MakeRegisterAdminWindow(strIdList)

	# テキストボックスで UnDo(ctrl-z) を有効にする．
	multiline = window["ID_list"].Widget  # この2行がポイント
	multiline.configure(undo=True)

	while True:
		event, values = window.read(timeout=500, timeout_key="-timeout-")

		if event == "register":
			strIdList = values["ID_list"]
			strIdList += "\n"

			if cCtrlCard.readCardInfo():
				strNewID = cCtrlCard.getID()
				strIdList += strNewID

			window["ID_list"].Update(strIdList)

		elif event == "end":
			strIdList = values["ID_list"]
			break

	# IDのリストを保存
	strIdList = strIdList.replace(" (used for activation)", "")
	listCardID = strIdList.split()
	with open(strFilePath, "w") as f:
		yaml.dump({"card_ID": listCardID}, f)

	window.close()
	cCtrlCard.finalize()


# カード編集 =============================================
def Edit_Card(cLogger):
	dictFlag = GetDictFlag()
	winSetCard, winEdit = MakeEditWindow(dictFlag)
	cCtrlCard = ClsNtagIF(cLogger, dictFlag, True)

	# 初期画面を設定
	winEdit.hide()
	window = winSetCard
	while True:
		event, values = window.read(timeout=500, timeout_key="-timeout-")

		if event == "edit":
			if cCtrlCard.readCardInfo() == True:
				if cCtrlCard.readCardRecord() == True:
					# Edit画面での編集可能な項目一覧を取得
					_, window_element_list = winEdit.read(timeout=0)
					window_element_list = window_element_list.keys()

					# カードから記録を読み出し
					dictSaveData = cCtrlCard.getRecord()

					# カードに記録されている値を初期値として設定
					for key, val in dictSaveData.items():
						if key in window_element_list:
							if val == "T":
								winEdit[key].update(True)
							else:
								winEdit[key].update(False)

			# 編集画面に移行
			winSetCard.hide()
			winEdit.un_hide()
			window = winEdit

		elif event == "write":
			if cCtrlCard.readCardInfo():
				if cCtrlCard.isWritable():
					strRecordToWrite = ""
					for key, val in values.items():
						if val is True:
							strRecordToWrite += "T"
						else:
							strRecordToWrite += "0"
					while len(strRecordToWrite) < 16:
						strRecordToWrite += "0"
					cCtrlCard.writeRecordDirect(strRecordToWrite)

		elif event == "return":
			# 初期画面に移行
			winEdit.hide()
			winSetCard.un_hide()
			window = winSetCard

		elif event == "end":
			break

	winSetCard.close()
	winEdit.close()
	cCtrlCard.finalize()


# メイン画面（動作選択） =============================================
def AdminModeIndependent():
	window = MakeMainWindow()
	cLogger = ClsLogger("tOITe-Admin")

	while True:
		event, values = window.read(timeout=500, timeout_key="-timeout-")

		if event == "end":
			window.close()
			return "end"

		elif event == "reset":
			window.close()
			return "reset"

		elif event == "register":
			window.hide()
			Register_Admin_Card(cLogger)
			window.un_hide()

		elif event == "edit":
			window.hide()
			Edit_Card(cLogger)
			window.un_hide()
