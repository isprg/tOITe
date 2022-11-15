import pyaudio
import os
import math
import time
import numpy as np
from scipy.io.wavfile import read 
from concurrent.futures import ThreadPoolExecutor
from alsa_error_handler import noalsaerr
from ClsLogger import ClsLogger


class ClsAudioOutBt:
	def __init__(self, cLogger):
		self.logger = cLogger
		self.sNumOfChannel = 1
		self.sSampleRate = 44100
		self.sToneAmplitude = 0.1
		self.blSoundEnd = False
		self.blExecutorWorking = False
		self.blKeepAlive = False
		self.sCountAlive = 0

		if os.name == 'nt':
			self.audio = pyaudio.PyAudio()
		else:
			with noalsaerr():
				self.audio = pyaudio.PyAudio()

		self.openStream()

	def __del__(self):
		self.finalize()

	def finalize(self):
		self.closeStream()
		self.audio.terminate()

	def shutdownThread(self):
		if self.blExecutorWorking == True:
			self.executor.shutdown()
			self.blExecutorWorking = False
		
		if self.blKeepAlive == True:
			self.blKeepAlive = False
			self.sCountAlive = 0

	def readWaveData(self, strFileName):
		try:
			self.sSampleRate, vSound = read(strFileName) 
			self.vSound = vSound / np.max(np.abs(vSound))
			self.sNumOfChannel = len(self.vSound.shape)
			self.sSoundLength = self.vSound.shape[0] / self.sSampleRate
			self.logger.logDebug("Read ", strFileName, ": ", self.sSampleRate, "[Hz], ", self.sSoundLength, "[s]")
		except Exception as ex:
			self.logger.logDebug(str(ex))
			self.sSampleRate = 0

	def openStream(self):
		self.stream = self.audio.open(
			format		=pyaudio.paFloat32,
			channels	=self.sNumOfChannel, 
			rate		=self.sSampleRate,
			input		=False,
			output		=True,
			start		=True)
		self.blStreamOpen = True

	def closeStream(self):
		if self.blStreamOpen:
			self.stream.stop_stream()
			self.stream.close()

	def getSoundEnd(self):
		return self.blSoundEnd

	def playBufferedSound(self):
		self.blSoundEnd = False
		self.stream.write(self.vSound.astype(np.float32).tobytes())
		self.blSoundEnd = True

	def playSound(self, strFileName):
		self.readWaveData(strFileName)
		if self.sSampleRate != 0:
			self.playBufferedSound()

	def playSoundAsync(self, strFileName):
		self.shutdownThread()
		self.blExecutorWorking = True
		self.executor = ThreadPoolExecutor(max_workers=1)
		self.executor.submit(self.playSound, strFileName)

	def getKeepAlive(self):
		return self.blKeepAlive
		
	def setKeepAlive(self, blKeepAlive):
		self.blKeepAlive = blKeepAlive

	def makeTone(self):
		sPlayTime = 2
		sFreq = 440
		vTime = np.linspace(0, sPlayTime, self.sSampleRate * sPlayTime)
		self.vSound = self.sToneAmplitude * np.sin(2 * math.pi * sFreq * vTime)

	def startKeepAlive(self, sWaitSecond):
		self.shutdownThread()
		self.blExecutorWorking = True
		self.blKeepAlive = True
		self.makeTone()
		self.executor = ThreadPoolExecutor(max_workers=1)
		self.executor.submit(self.playKeepAliveTone, sWaitSecond)

	def playKeepAliveTone(self, sWaitSecond):
		sSleepTime = 0.5
		self.sCountAlive = 0
		while True:
			time.sleep(sSleepTime)
			self.sCountAlive += sSleepTime
			print(self.sCountAlive)
			if self.sCountAlive >= sWaitSecond:
				self.playBufferedSound()
				self.sCountAlive = 0
			if self.blKeepAlive == False:
				break


if __name__ == '__main__':
	from ClsAudioOut import ClsAudioOut
	from ClsLogger import ClsLogger
	import time

	cLogger = ClsLogger()
	cAudioOut = ClsAudioOutBt(cLogger)
	#cAudioOut.readWaveData("card_set.wav")
	#cAudioOut.playSound("tutorial1.wav")
	cAudioOut.playSound("card_set.wav")
	cAudioOut.playSound("card_set0.wav")
	cAudioOut.startKeepAlive(5)
	time.sleep(17)
	cAudioOut.setKeepAlive(False)
	#print("first timer end")
	#cAudioOut.startKeepAlive(5)
	#time.sleep(17)
	#cAudioOut.setKeepAlive(False)
	cAudioOut.finalize()
