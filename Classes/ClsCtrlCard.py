from Classes.ClsCardIF import ClsCardIF


class ClsCtrlCard:
	def __init__(self, dictFlag):
		self.ClsCardIF = ClsCardIF()

		self.ClsCardIF.open()
		self.CurrentID = None

		# 記録と問題名の対応を表すテーブル
		self.dictFlagRecord = {}
		for key in dictFlag:
			self.dictFlagRecord[key] = "0"

	def Finalize(self):
		self.ClsCardIF.close()

	def setCard(self):
		if self.ClsCardIF.sense() is None:
			return False
		else:
			self.CurrentID = self.ClsCardIF.getID()
			self.updata_record_table()

			return True

	def reset_record_table(self):
		for key in self.dictFlagRecord.keys():
			self.dictFlagRecord[key] = "0"

	def initCard(self):
		bSuccess = self.ClsCardIF.initTag(force=True)

		# 初期化失敗時に1度はリトライする
		if not bSuccess:
			bSuccess = self.retry_to_initCard()

		if bSuccess:
			self.reset_record_table()

		return bSuccess

	def retry_to_initCard(self):
		print("retry to initCard")
		self.ClsCardIF.sense()
		return self.ClsCardIF.initTag(force=True)

	def initID(self):
		self.ClsCardIF.initID()

	def getID(self):
		return self.CurrentID

	def write_result(self, strFlagName, strAns):
		if strFlagName not in self.dictFlagRecord:
			return False

		sNumOfFlags = list(self.dictFlagRecord.keys()).index(
			strFlagName
		)  # 問題名から対応する番号を取得
		bSuccess = self.ClsCardIF.writeAnswer(sNumOfFlags, strAns)  # カードに書き込み

		# 書き込み失敗時に1度はリトライする
		if not bSuccess:
			bSuccess = self.retry_to_write()

		if bSuccess:
			self.dictFlagRecord[strFlagName] = strAns

		return bSuccess

	def retry_to_write(self):
		print("retry to write")
		self.ClsCardIF.sense()
		self.ClsCardIF.initTag(force=True)

		bSuccess = True
		for sNumOfFlags, strAns in enumerate(self.dictFlagRecord.values()):
			if not self.ClsCardIF.writeAnswer(sNumOfFlags, strAns):
				bSuccess = False

		return bSuccess

	def updata_record_table(self):
		record = self.ClsCardIF.readRecord()

		if record is None:
			# 読み込み失敗時に1度はリトライする
			print("retry to read")
			self.ClsCardIF.sense()
			record = self.ClsCardIF.readRecord()

			if record is None:
				self.reset_record_table()
		else:
			for i, key in enumerate(self.dictFlagRecord.keys()):
				self.dictFlagRecord[key] = record[i]

	def read_result(self):
		return self.dictFlagRecord.copy()

	def check_exist(self):
		if self.ClsCardIF.sense() is None:
			return False
		else:
			return True

	def check_identity(self):
		self.ClsCardIF.sense()

		if self.CurrentID != self.ClsCardIF.getID():
			return False
		else:
			return True
