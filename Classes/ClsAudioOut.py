import os
import subprocess
from concurrent.futures import ThreadPoolExecutor


class ClsAudioOut:
	def __init__(self, cLogger):
		self.blSoundEnd = False
		self.blExecutorWorking = False
		self.blStateChange = False
		self.logger = cLogger

	def setDictArgument(self, dictArgument):
		self.dictArgument = dictArgument

	def setClsCtrlState(self, cState):
		self.cState = cState

	def playSound(self, *tplFileName):
		self.blSoundEnd = False
		for strFileName in tplFileName:
			if os.name != 'nt':
				subprocess.run(["aplay", "--quiet", strFileName])
			else:
				subprocess.run(
				["powershell", "-c", f"(New-Object Media.SoundPlayer '{strFileName}').PlaySync();"])
		self.blSoundEnd = True

		if self.blStateChange:
			self.dictArgument["Start time"] = self.cState.updateState(self.strNextState)
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
	from ClsAudioOut import ClsAudioOut
	from ClsLogger import ClsLogger
	import time

	cLogger = ClsLogger()
	cAudioOut = ClsAudioOut(cLogger)
	cAudioOut.playSoundAsync("sound/correct_24.wav", "sound/wrong_24.wav")
	cAudioOut.playSoundAsync("sound/card_set_24.wav")
	time.sleep(2)
	cAudioOut.shutdownThread()
	cAudioOut.playSound("sound/tutorial2_24.wav")
