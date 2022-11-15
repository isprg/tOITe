import cv2
import numpy as np

from ClsImageProcess import ClsImageProcess


class ClsImageProcessQR(ClsImageProcess):
	def process(self):
		isFound = False
		imGray = cv2.cvtColor(self.imSensor, cv2.COLOR_BGR2GRAY)
		qr = cv2.QRCodeDetector()
		data, points, straight_qrcode = qr.detectAndDecode(imGray)
		if 'LenaKnows' in data:
			pts = points.astype(np.int32)
			self.imProcessed= cv2.polylines(self.imSensor, [pts], True,(0,0,255), 2, cv2.LINE_AA)
			self.sCounter = self.sCounter + 1
			if self.sCounter > 5:
				self.sCounter = 0
				isFound = True
		else:
			self.imProcessed = self.imSensor

		return isFound


if __name__ == '__main__':
	import ClsImageProcessQR as CProc
	import cv2

	strPlatform = 'WIN'
	sCameraNumber = 0
	sSensorWidth = 640
	sSensorHeight = 480
	sMonitorWidth = 1920
	sMonitorHeight = 1280
	tplWindowName = ('full',)
	sFlipMode = 2

	proc = CProc.ClsImageProcessQR(
		strPlatform, 
		sCameraNumber,
		sSensorWidth, 
		sSensorHeight, 
		sMonitorWidth, 
		sMonitorHeight,
		tplWindowName,
		sFlipMode)

	proc.createWindows()

	while True:
		proc.execute()
		sKey = cv2.waitKey(1) & 0xFF
		if sKey == ord('q'):
			del proc
			break