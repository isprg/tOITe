import yaml

from Classes.ClsCardIF import ClsCardIF
from Classes.ClsCtrlCard import ClsCtrlCard
from functions.common import CheckComplete, getDictFlag
from functions.AdminModeWindow import *


# Adminカード登録 =============================================
def Register_Admin_Card(Activate_CardID):
	file_path = "files/Admin_CardID_list.yaml"
	with open(file_path, "r") as f:
		card_ID_list = yaml.safe_load(f)["card_ID"]

	text = ""
	for i in card_ID_list:
		if i == Activate_CardID:
			i += " (used for activation)"
		text += i
		text += "\n"

	window = MakeRegisterAdminWindow(text)

	# テキストボックスで UnDo(ctrl-z) を有効にする．
	multiline = window["ID_list"].Widget  # この2行がポイント
	multiline.configure(undo=True)

	# カード操作用のクラスを生成
	cCardIF = ClsCardIF()
	cCardIF.open()

	while True:
		event, values = window.read(timeout=500, timeout_key="-timeout-")

		if event == "register":
			text = values["ID_list"]
			text += "\n"

			if cCardIF.sense() is not None:
				NewID = cCardIF.getID()
				text += NewID

			window["ID_list"].Update(text)

		elif event == "end":
			text = values["ID_list"]
			break

	# IDのリストを保存
	text = text.replace(" (used for activation)", "")
	card_ID_list = text.split()
	with open(file_path, "w") as f:
		yaml.dump({"card_ID": card_ID_list}, f)

	window.close()
	cCardIF.close()


# カード編集 =============================================
def Edit_Card():
	dictFlag = getDictFlag()
	winSetCard, winEdit = MakeEditWindow(dictFlag)
	cCtrlCard = ClsCtrlCard(dictFlag)

	# 初期画面を設定
	winEdit.hide()
	window = winSetCard
	while True:
		event, values = window.read(timeout=500, timeout_key="-timeout-")

		if event == "edit":
			if cCtrlCard.setCard():
				# Edit画面での編集可能な項目一覧を取得
				_, window_element_list = winEdit.read(timeout=0)
				window_element_list = window_element_list.keys()

				# カードから記録を読み出し
				dictSaveData = cCtrlCard.read_result()

				# カードに記録されている値を初期値として設定
				for key, val in dictSaveData.items():
					if key in window_element_list and val == "T":
						winEdit[key].update(True)

			# 編集画面に移行
			winSetCard.hide()
			winEdit.un_hide()
			window = winEdit

		elif event == "write":
			if cCtrlCard.check_exist() and cCtrlCard.initCard():
				for key, val in values.items():
					if key in dictFlag and val is True:
						cCtrlCard.write_result(key, "T")

				# ゲームクリア状態になった場合，記録を追加
				bClear = CheckComplete(cCtrlCard, dictFlag)
				if bClear:
					cCtrlCard.write_result("complete", "T")
				else:
					cCtrlCard.write_result("complete", "0")
			else:
				print("failed to write")

		elif event == "return":
			# 初期画面に移行
			winEdit.hide()
			winSetCard.un_hide()
			window = winSetCard

		elif event == "end":
			break

	winSetCard.close()
	winEdit.close()
	cCtrlCard.Finalize()


# メイン画面（動作選択） =============================================
def AdminMode(Activate_CardID):
	window = MakeMainWindow()

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
			Register_Admin_Card(Activate_CardID)
			window.un_hide()

		elif event == "edit":
			window.hide()
			Edit_Card()
			window.un_hide()
