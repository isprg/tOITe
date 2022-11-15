import binascii
import nfc
from ndef import TextRecord


class ClsCardIF:
    def __init__(self):
        self.currentTag = None
        self.currentTagType = None
        self.currentIdm = None
        self.currentNdef = None
        self.hasChanged = False

    def __str__(self):
        return f"<{self.currentTagType} Idm={str(self.currentIdm)}>"

    def __enter__(self):
        # withによるインスタンス生成時処理
        self.open()
        return self

    def __exit__(self, *args):
        # *argsがないとclose時にエラーが発生し, 正常にcloseできません.
        self.close()

    def initID(self):
        self.currentIdm = None

    def getID(self) -> str or None:
        # タグのIDを文字列で返す関数
        return self.currentIdm

    def getAnswer(self, problem_number) -> str or None:
        # 回答履歴のrecordを取得,problem_numberは問題番号(0スタート)
        answer_history = self.readRecord()
        if answer_history == "" or answer_history is None:
            return None
        split_answer = list(answer_history)
        return split_answer[problem_number]

    def writeAnswer(self, problem_number, problem_answer) -> bool:
        # problem_numberは問題番号(0スタート), problem_answerは回答結果(1文字) ex. "C"
        answer_history = self.readRecord()
        if answer_history == "" or answer_history is None:
            return False
        if len(problem_answer) != 1:
            return False
        split_answer = list(answer_history)
        split_answer[problem_number] = problem_answer
        return self.writeRecord("".join(split_answer))

    def initTag(self, force=False):
        # recordを16個の0埋めにする関数
        if force is True:
            return self.writeRecord("0000000000000000")
        record = self.readRecord()
        if record == "" or record is None:
            return self.writeRecord("0000000000000000")

    def readRecord(self) -> str or None:
        # recordを返す.存在しない場合はNoneを返す.
        if self.currentTag is not None and self.currentNdef is not None:
            try:
                return self.currentNdef.records[0].text
            except TypeError:
                print("TypeError")
                return None
            except IndexError:
                print("IndexError")
                return None

        print("currentTag or CurrentNdef is None")
        return None

    def writeRecord(self, data) -> bool:
        # 書き込み成功でTrueを返す.
        if self.currentTag is None or self.currentNdef is None:
            return False
        if not self.currentNdef.is_writeable:
            return False
        if self.currentTagType == "Type2Tag":
            try:
                self.currentNdef.records = [TextRecord(data)]
                return True
            except nfc.tag.tt2.Type2TagCommandError:
                pass
            except TypeError:
                pass
        return False

    def open(self):
        self.clf = nfc.ContactlessFrontend("usb")

    def close(self):
        self.clf.close()

    def sense(self):
        target_res = self.clf.sense(
            nfc.clf.RemoteTarget("106A"),
            nfc.clf.RemoteTarget("106B"),
            iterations=1,
            interval=0.1,
        )
        if target_res is None:
            return None
        tag = nfc.tag.activate(self.clf, target_res)

        if tag is not None:
            if self.currentIdm != binascii.hexlify(tag._nfcid).decode():
                print(f"Touched : {binascii.hexlify(tag._nfcid).decode()}\n{tag}")
                self.currentTag = tag
                self.currentTagType = tag.type
                self.currentIdm = binascii.hexlify(tag._nfcid).decode()
                if tag.ndef:
                    self.currentNdef = tag.ndef
                self.hasChanged = True
            else:
                self.hasChanged = False
            return tag
        return None


if __name__ == "__main__":
    with ClsCardIF() as cif:
        while True:
            cif.sense()  # ntag215の読み取り
            idm = cif.getID()  # 必ずcif.senseの後に呼び出す
            record = cif.readRecord()  # records読み出し
            if record is not None:
                print(f"Record : {record}")
            cif.writeAnswer(0, "T")  # record書き込み
