class ClsNtagIF:
    def __init__(self, cLogger, dictFlag, blWriteEnable):
        self.logger = cLogger
        self.strCardID = "DummyCard"

        # 記録と問題名の対応を表すテーブル
        self.dictFlagRecord = {}
        for key in dictFlag:
            self.dictFlagRecord[key] = "0"
        self.dictFlagRecord["tutorial"] = "T"
        #self.dictFlagRecord["pose"] = "T"

    def __del__(self):
        self.finalize()

    def finalize(self):
        pass

    def senseCard(self):
        return True

    def readCardInfo(self):
        return True

    def readCardRecord(self):
        return 1

    def isReadable(self):
        return True

    def isWritable(self):
        return True

    def getRecord(self):
        return self.dictFlagRecord.copy()

    def initID(self):
        self.strCardID = None
        self.strCardIDBuf = None

    def keepID(self):
        self.strCardIDBuf = self.strCardID

    def getID(self):
        return self.strCardID

    def checkIdentity(self):
        return True

    def initRecord(self):
        for key in self.dictFlagRecord.keys():
            self.dictFlagRecord[key] = "0"

    def writeCardRecord(self, strFlagName, strValue):
        if strFlagName in self.dictFlagRecord:
            self.dictFlagRecord[strFlagName] = strValue
        else:
            self.logger.logDebug("No such flag.")

    def writeRecordDirect(self, strRecord):
        pass

    def checkComplete(self):
        blClear = True
        for key in self.dictFlagRecord.keys():
            if self.dictFlagRecord[key] != "T":
                blClear = False
                break

        return blClear
