import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import read
from concurrent.futures import ThreadPoolExecutor


class ClsAudioOut:
    def __init__(self, cLogger):
        self.blSoundEnd = False
        self.blExecutorWorking = False
        self.blStateChange = False
        self.logger = cLogger
        if os.name != 'nt':
            sd.default.device = [15, 15]  # Input, Outputデバイス指定
        else:
            sd.default.device = [1, 3]
        sd.query_devices(device=sd.default.device[1])

    def setDictArgument(self, dictArgument):
        self.dictArgument = dictArgument

    def setClsCtrlState(self, cState):
        self.cState = cState

    def playSound(self, *tplFileName):
        self.blSoundEnd = False
        for strFileName in tplFileName:
            sSampleRate, vSound = read(strFileName)
            vSound = vSound / np.max(np.abs(vSound))
            sd.play(vSound, sSampleRate)
            sd.wait()
        self.blSoundEnd = True

        if self.blStateChange:
            self.dictArgument["Start time"] = self.cState.updateState(
                self.strNextState)
            self.blStateChange = False

    def getSoundEnd(self):
        return self.blSoundEnd

    def playSoundAsync(self, *tplFileName):
        self.shutdownThread()
        self.blExecutorWorking = True
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor.submit(self.playSound, *tplFileName)

    def shutdownThread(self):
        if self.blExecutorWorking == True:
            self.executor.shutdown()
            self.blExecutorWorking = False

    def enableStateChange(self, strNextState):
        self.blStateChange = True
        self.strNextState = strNextState


if __name__ == '__main__':
    from ClsAudioOutSd import ClsAudioOut
    from ClsLogger import ClsLogger
    import time

    cLogger = ClsLogger()
    cAudioOut = ClsAudioOut(cLogger)
    cAudioOut.playSoundAsync("sound/correct_24.wav", "sound/wrong_24.wav")
    cAudioOut.playSoundAsync("sound/card_set_24.wav")
    time.sleep(2)
    cAudioOut.shutdownThread()
    cAudioOut.playSound("sound/tutorial2_24.wav")
