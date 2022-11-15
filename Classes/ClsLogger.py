import os
import datetime
from logging import NOTSET, getLogger, StreamHandler, FileHandler, Formatter, DEBUG


class ClsLogger:
	def __init__(self):
		self.logger = getLogger("tOITe-Log")
		self.logger.setLevel(DEBUG)
		self.hStream = StreamHandler()
		self.hStream.setLevel(DEBUG)
		formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		self.hStream.setFormatter(formatter)
		self.logger.addHandler(self.hStream)

		strLogPath = "files/log/"
		os.makedirs(strLogPath, exist_ok=True)
		strNow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
		strFileName = strLogPath + strNow + ".log"
		self.hFile = FileHandler(filename=strFileName)
		self.hFile.setLevel(DEBUG)
		self.hFile.setFormatter(formatter)
		self.logger.addHandler(self.hFile)

	def logDebug(self, *tplLogForDebug):
		strLogAll = ""
		for strLog in tplLogForDebug:
			if type(strLog) is float:
				strLog = '{:.2f}'.format(strLog)
			strLogAll = strLogAll + str(strLog)
		self.logger.debug(strLogAll)


if __name__ == '__main__':
	from ClsLogger import ClsLogger


