import cv2
import numpy as np


class ClsWindow:
	def __init__(self, tplWindowName, sFlipEnable):
		self.active = False
		self.sFlipEnable = sFlipEnable
		self.tplWindowName = tplWindowName
		self.enableOverlay = False
		self.sWidthDiff = 0
		self.sHeightDiff = 0
	
	def __del__(self):
		self.closeWindows()
	
	def Finalize(self):
		self.closeWindows()
	
	def createWindows(self):
		if self.active == False:
			for strWindowName in self.tplWindowName:
				cv2.namedWindow(strWindowName, cv2.WINDOW_NORMAL)
				if strWindowName == 'full':
					cv2.setWindowProperty(strWindowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
			self.active = True

	def prepareFullScreen(self, sMonitorWidth, sMonitorHeight, sImageWidth, sImageHeight):
		sRatioWidth = sMonitorWidth / sImageWidth
		sRatioHeight = sMonitorHeight / sImageHeight
		if sRatioWidth > sRatioHeight:
			self.sRatioFull = sRatioHeight
			self.sBlankMode = 1
			sBlankWidth = (int) ((sMonitorWidth - self.sRatioFull * sImageWidth) / 2)
			self.imBlank = np.uint8(np.zeros((sMonitorHeight, sBlankWidth, 3)))
			self.sWidthDiff = sMonitorWidth - self.sRatioFull * sImageWidth - 2 * sBlankWidth
		elif sRatioWidth < sRatioHeight:
			self.sRatioFull = sRatioWidth
			self.sBlankMode = 2
			sBlankHeight = (int) ((sMonitorHeight - self.sRatioFull * sImageHeight) / 2)
			self.imBlank = np.uint8(np.zeros((sBlankHeight, sMonitorWidth, 3)))
			self.sHeightDiff = sMonitorHeight - self.sRatioFull * sImageHeight - 2 * sBlankHeight
		else:
			self.sRatioFull = sRatioWidth
			self.sBlankMode = 0

	def imshow(self, strWindowName, imDisplay):
		if self.active == True:
			if strWindowName == 'full':
				if self.sFlipEnable == True:
					imDisplay = cv2.flip(imDisplay, 1)
				sWidthFit = (int) (self.sRatioFull * imDisplay.shape[1] + self.sWidthDiff)
				sHeightFit = (int) (self.sRatioFull * imDisplay.shape[0] + self.sHeightDiff)
				imDisplay = cv2.resize(imDisplay, (sWidthFit, sHeightFit))
				if self.sBlankMode == 1:
					imDisplay = np.concatenate([self.imBlank, imDisplay, self.imBlank], 1)
				elif self.sBlankMode == 2:
					imDisplay = np.concatenate([self.imBlank, imDisplay, self.imBlank], 0)
				if self.enableOverlay:
					imDisplay[	self.sOverlayTop : self.sOverlayTop + self.imOverlay.shape[0], 
								self.sOverlayLeft : self.sOverlayLeft + self.imOverlay.shape[1]] \
								*= 1 - self.imOverlayMask.astype('uint8')
					imDisplay[	self.sOverlayTop : self.sOverlayTop + self.imOverlay.shape[0], 
								self.sOverlayLeft : self.sOverlayLeft + self.imOverlay.shape[1]] \
								+= 	self.imOverlay * self.imOverlayMask.astype('uint8')
				cv2.imshow(strWindowName, imDisplay)
			else:
				cv2.imshow(strWindowName, imDisplay)

	def setEnableOverlay(self, enableOverlay, sOverlayLeft, sOverlayTop):
		self.enableOverlay = enableOverlay
		self.sOverlayLeft = sOverlayLeft
		self.sOverlayTop = sOverlayTop

	def setOverlayImage(self, imOverlay, imOverlayMask):
		self.imOverlay = imOverlay
		self.imOverlayMask = imOverlayMask
		
	def closeWindows(self):
		if self.active == True:
			for strWindowName in self.tplWindowName:
				cv2.destroyWindow(strWindowName)
				cv2.waitKey(1)
		self.active = False


