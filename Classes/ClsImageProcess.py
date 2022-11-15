from ClsImageSensor import ClsImageSensor
from ClsWindow import ClsWindow


class ClsImageProcess:
	def __init__(
		self,
		strPlatform,
		sCameraNumber,
		sWidthSensor,
		sHeightSensor,
		sWidthWindow,
		sHeightWindow,
		tplWindowName,
		sFlipMode,
	):
		if sFlipMode == 1:
			sSensorFlip = True
			sMonitorFlip = False
		elif sFlipMode == 2:
			sSensorFlip = False
			sMonitorFlip = True
		else:
			sSensorFlip = False
			sMonitorFlip = False

		self.tplWindowName = tplWindowName
		self.sensor = ClsImageSensor(
			strPlatform, sCameraNumber, sWidthSensor, sHeightSensor, sSensorFlip
		)
		sWidthInput, sHeightInput = self.sensor.getImageSize()
		self.window = ClsWindow(tplWindowName, sMonitorFlip)
		self.window.prepareFullScreen(
			sWidthWindow, sHeightWindow, sWidthInput, sHeightInput
		)
		self.sCounter = 0
		self.initProcess()

	def __del__(self):
		self.termProcess()
		del self.sensor
		del self.window

	def Finalize(self):
		self.termProcess()
		self.sensor.Finalize()
		self.window.Finalize()

	def initProcess(self):
		self.initproc = False

	def termProcess(self):
		self.termproc = False

	def createWindows(self):
		self.window.createWindows()

	def closeWindows(self):
		self.window.closeWindows()

	def execute(self):
		self.imSensor = self.sensor.read()
		result = self.process()
		for strWindowName in self.tplWindowName:
			self.window.imshow(strWindowName, self.imProcessed)
		return result

	def process(self):
		self.imProcessed = self.imSensor
		return 0


if __name__ == "__main__":
	import cv2
	from ClsImageProcess import ClsImageProcess

	strPlatform = "WIN"
	sCameraNumber = 0
	sSensorWidth = 640
	sSensorHeight = 480
	sMonitorWidth = 1920
	sMonitorHeight = 1280
	tplWindowName = ("full",)
	sFlipMode = 1

	proc = ClsImageProcess(
		strPlatform,
		sCameraNumber,
		sSensorWidth,
		sSensorHeight,
		sMonitorWidth,
		sMonitorHeight,
		tplWindowName,
		sFlipMode,
	)

	proc.createWindows()

	while True:
		proc.execute()
		sKey = cv2.waitKey(1) & 0xFF
		if sKey == ord("q"):
			del proc
			break
