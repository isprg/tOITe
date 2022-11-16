import binascii
import nfc
from ndef import TextRecord


class ClsNtagIF:
    def __init__(self, cLogger, dictFlag, blPlayCardEnable):
        self.logger = cLogger

        self.clf = nfc.ContactlessFrontend("usb")
        self.strCardID = None
        self.strCardIDBuf = None
        self.senseResult = None

        self.cardTag = None
        self.strRecord = None
        self.cardReadable = False
        self.cardWritable = False
        self.blPlayCardEnable = blPlayCardEnable

        # 記録と問題名の対応を表すテーブル
        self.dictFlagRecord = {}
        for key in dictFlag:
            self.dictFlagRecord[key] = "0"

    def __del__(self):
        self.finalize()

    def finalize(self):
        self.clf.close()

    def senseCard(self):
        self.senseResult = self.clf.sense(
            nfc.clf.RemoteTarget("106A"),
            nfc.clf.RemoteTarget("106B"),
            iterations=1,
            interval=0.1,
        )

        if self.senseResult is None:
            return False
        else:
            return True

    def readCardInfo(self):
        self.cardReadable = False
        self.cardWritable = False

        if self.senseCard():
            tag = nfc.tag.activate(self.clf, self.senseResult)

            if tag is None:
                self.logger.logDebug("NFC is not available.")
            elif tag.type != "Type2Tag":
                self.logger.logDebug("NFC is not Type2")
            elif tag.ndef is None:
                self.logger.logDebug("NDEF is not available.")
            else:
                self.cardReadable = True
                if tag.ndef.is_writeable:
                    self.cardWritable = True

            if self.cardReadable:
                if self.strCardID != binascii.hexlify(tag._nfcid).decode():
                    self.logger.logDebug(
                        f"Touched : {binascii.hexlify(tag._nfcid).decode()}\n{tag}")
                    self.cardTag = tag
                    self.strCardID = binascii.hexlify(tag._nfcid).decode()
                return True
            else:
                return False
        else:
            return False

    def readCardRecord(self):
        if self.blPlayCardEnable:
            if self.cardReadable:
                return self.readNdefRecords()
            else:
                return False
        else:
            return False

    def readNdefRecords(self):
        try:
            self.strRecord = self.cardTag.ndef.records[0].text
            if self.strRecord is not None:
                self.logger.logDebug("RD Record :" + self.strRecord)
                for i, key in enumerate(self.dictFlagRecord.keys()):
                    self.dictFlagRecord[key] = self.strRecord[i]
                return True
            else:
                self.logger.logDebug("No record")
                return False
        except TypeError:
            self.logger.logDebug("TypeError")
            return False
        except IndexError:  # Blank card
            self.logger.logDebug("IndexError")
            return False

    def isReadable(self):
        return self.cardReadable

    def isWritable(self):
        return self.cardWritable

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
        self.readCardInfo()

        if self.strCardID != self.strCardIDBuf:
            return False
        else:
            return True

    def initRecord(self):
        if self.blPlayCardEnable:
            self.readCardInfo()

            if self.cardWritable:
                self.cardTag.ndef.records = [TextRecord("0000000000000000")]
                for key in self.dictFlagRecord.keys():
                    self.dictFlagRecord[key] = "0"

    def writeCardRecord(self, strFlagName, strValue):
        if self.blPlayCardEnable:
            self.readCardInfo()

            if self.cardReadable and self.cardWritable:
                self.readNdefRecords()
                listRecord = list(self.strRecord)

                if strFlagName in self.dictFlagRecord:
                    sNumOfFlags = list(
                        self.dictFlagRecord.keys()).index(strFlagName)
                    self.dictFlagRecord[strFlagName] = strValue
                    listRecord[sNumOfFlags] = strValue
                    dataToWrite = "".join(listRecord)
                    self.cardTag.ndef.records = [TextRecord(dataToWrite)]
                else:
                    self.logger.logDebug("No such flag.")
            else:
                self.logger.logDebug("NFC is not available.")

    def writeRecordDirect(self, strRecord):
        if self.blPlayCardEnable:
            self.readCardInfo()

            if self.cardWritable:
                self.cardTag.ndef.records = [TextRecord(strRecord)]
                self.logger.logDebug("WR Record :" + strRecord)

    def checkComplete(self):
        blClear = True
        for key in self.dictFlagRecord.keys():
            if self.dictFlagRecord[key] != "T":
                blClear = False
                break

        return blClear


if __name__ == "__main__":
    import time
    from ClsLogger import ClsLogger

    dictFlag = {
        "tutorial": "チュートリアル",
        "speech": "音声認識",
        "pose": "姿勢推定",
        "select": "多岐選択",
        "complete": "クリア",
    }

    cLogger = ClsLogger("tOITe-log")
    cNtag = ClsNtagIF(cLogger, dictFlag)
    while True:
        if cNtag.readCardInfo():
            cNtag.readCardRecord()
            print("Flag ID:")
            strNameOfFlag = input()
            if strNameOfFlag == "exit":
                break
            print("Record value:")
            sValueOfRecord = input()
            cNtag.writeCardRecord(strNameOfFlag, sValueOfRecord)
        time.sleep(1)
