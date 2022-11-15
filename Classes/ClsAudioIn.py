import pyaudio
import wave
import os
from concurrent.futures import ThreadPoolExecutor
from alsa_error_handler import noalsaerr


class ClsAudioIn:
	def __init__(self, cLogger, sChannels, sRate, sUnitSample):
		self.logger = cLogger
		self.vAudio = []
		self.blRecording = False
		self.blExecutorWorking = False
		self.format = pyaudio.paInt16
		self.sChannels = sChannels
		self.sRate = sRate
		self.sUnitSample = sUnitSample

		if os.name == 'nt':
			self.audio = pyaudio.PyAudio()
		else:
			with noalsaerr():
				self.audio = pyaudio.PyAudio()

	def __del__(self):
		self.finalize()

	def finalize(self):
		self.audio.terminate()

	def initBuffer(self):
		self.vAudio = []

	def startRecordThread(self):
		self.shutdownRecordThread()

		self.stream = self.audio.open(
			format=pyaudio.paInt16,
			channels=self.sChannels,
			rate=self.sRate,
			input=True,
			output=False,
			frames_per_buffer=self.sUnitSample)
			
		self.vAudio = []
		self.blRecording = True
		self.blExecutorWorking = True
		self.logger.logDebug("Audio record thread was started")
		self.executor = ThreadPoolExecutor(max_workers=1)
		self.executor.submit(self.sample)

	def shutdownRecordThread(self):
		if self.blExecutorWorking == True:
			self.executor.shutdown()
			self.blExecutorWorking = False

	def setRecording(self, blRecording):
		self.blRecording = blRecording

	def getRecording(self):
		return self.blRecording

	def sample(self):
		while self.blRecording:
			vData = self.stream.read(self.sUnitSample)
			self.vAudio.append(vData)

		self.stream.stop_stream()
		self.stream.close()

	def record(self, strFileName):
		wf = wave.open(strFileName, 'wb')
		wf.setnchannels(self.sChannels)
		wf.setsampwidth(self.audio.get_sample_size(self.format))
		wf.setframerate(self.sRate)
		wf.writeframes(b''.join(self.vAudio))
		wf.close()


if __name__ == '__main__':
	from ClsAudioIn import ClsAudioIn
	import time

	sChannels = 1
	sRate = 22050
	sUnitSample = 1024

	cAudioIn = ClsAudioIn(sChannels, sRate, sUnitSample)
	cAudioIn.startRecordThread()
	time.sleep(5)
	cAudioIn.setRecording(False)
	cAudioIn.record("test1.wav")
	cAudioIn.finalize()