import time
import cv2
import mediapipe as mp
from numpy import uint8
from ClsImageProcess import ClsImageProcess
from JudgePose import judge_pose


class ClsImageProcessPose(ClsImageProcess):
	def initProcess(self):
		self.isROIdefined = False
		self.ratioROI = 0.5
		self.blPoseCorrect = False  # ポーズができたかのフラグ
		self.sTimeAtCorrect = 0  # ポーズができた時の時間を格納する場所
		self.sJudgeMargin = 20
		self.mp_pose = mp.solutions.pose
		self.pose = self.mp_pose.Pose(
			min_detection_confidence=0.5,
			min_tracking_confidence=0.5)

		imOverlayOrig_inst = cv2.imread('./images/sign_inst2.png', -1)
		self.imOverlayMask_inst = imOverlayOrig_inst[:,:,3]
		self.imOverlayMask_inst = cv2.cvtColor(self.imOverlayMask_inst, cv2.COLOR_GRAY2BGR)
		self.imOverlayMask_inst	 = self.imOverlayMask_inst / 255
		self.imOverlayOrig_inst = imOverlayOrig_inst[:,:,:3]
		# self.window.setEnableOverlay(True, 300, 0)
		# self.window.setOverlayImage(self.imOverlayOrig_inst, self.imOverlayMask_inst)

		imOverlayOrig_correct = cv2.imread('./images/sign_correct_cyan.png', -1)
		self.imOverlayMask_correct = imOverlayOrig_correct[:,:,3]
		self.imOverlayMask_correct = cv2.cvtColor(self.imOverlayMask_correct, cv2.COLOR_GRAY2BGR)
		self.imOverlayMask_correct	 = self.imOverlayMask_correct / 255
		self.imOverlayOrig_correct = imOverlayOrig_correct[:,:,:3]
		self.window.setEnableOverlay(True, 0, 0)
		# self.window.setOverlayImage(self.imOverlayOrig_correct, self.imOverlayMask_inst)
	
	def setRatioROI(self, ratioROI):
		self.ratioROI = ratioROI

	def defineCorrectPose(self):
		self.correctAngles = list(range(8))
		self.correctAngles[0] = 143.5885
		self.correctAngles[1] = 151.5676
		self.correctAngles[2] = 176.0291
		self.correctAngles[3] = 183.4004
		self.correctAngles[4] = 141.0687
		self.correctAngles[5] = 161.5590
		self.correctAngles[6] = 185.0458
		self.correctAngles[7] = 170.7074	
		print(self.correctAngles)
	
	def defineROI(self, img):
		width = int(img.shape[1] * self.ratioROI)
		self.leftPosROI = int((img.shape[1] - width) / 2)
		self.rightPosROI = img.shape[1] - self.leftPosROI
		self.isROIdefined = True

	def reset(self):
		self.blPoseCorrect = False  # ポーズができたかのフラグ
		self.sTimeAtCorrect = 0  # ポーズができた時の時間を格納する場所

	def drawLandamrks(self, vPoints, sLineWidth, vLineColor, sCircleRadius, vCircleColor):
		self.drawLine(vPoints[11], vPoints[12], sLineWidth, vLineColor)
		self.drawLine(vPoints[11], vPoints[23], sLineWidth, vLineColor)
		self.drawLine(vPoints[12], vPoints[24], sLineWidth, vLineColor)
		self.drawLine(vPoints[23], vPoints[24], sLineWidth, vLineColor)

		for i, point in enumerate(vPoints):
			if 0 <= point[0] <= self.imSensor.shape[1] and 0<= point[1] <= self.imSensor.shape[0]:
				if 11 <= i <= 14 or 23 <= i <= 26:
					self.drawLine(vPoints[i], vPoints[i + 2], sLineWidth, vLineColor)
					cv2.circle(self.imSensor, 
						center=point, 
						radius=sCircleRadius, 
						color=vCircleColor, 
						thickness=-1, 
						lineType=cv2.LINE_4)

	def drawLine(self, vPoint1, vPoint2, sLineWidth, vLineColor):
		cv2.line(self.imSensor, vPoint1, vPoint2, 
				color=vLineColor, 
				thickness=sLineWidth, 
				lineType=cv2.LINE_4)

	def process(self):
		if self.isROIdefined == False:
			self.defineROI(self.imSensor)
		imROI = self.imSensor[:, self.leftPosROI:self.rightPosROI]

		# ランドマーク取得
		imROI = cv2.cvtColor(imROI, cv2.COLOR_BGR2RGB)
		imROI.flags.writeable = False
		results = self.pose.process(imROI)
		imROI.flags.writeable = True
		imROI = cv2.cvtColor(imROI, cv2.COLOR_RGB2BGR)

		# ROI以外を暗く
		self.imSensor[:,:self.leftPosROI] = (self.imSensor[:,:self.leftPosROI]*0.5).astype(uint8)
		self.imSensor[:,self.rightPosROI:] = (self.imSensor[:,self.rightPosROI:]*0.5).astype(uint8)

		# ROIの左右に黄色の線を引く
		self.imSensor = cv2.line(self.imSensor, (self.leftPosROI, 0), (
			self.leftPosROI, self.imSensor.shape[0]), (0, 0, 255), thickness=2, lineType=cv2.LINE_8)
		self.imSensor = cv2.line(self.imSensor, (self.rightPosROI, 0), (
			self.rightPosROI, self.imSensor.shape[0]), (0, 0, 255), thickness=2, lineType=cv2.LINE_8)

		if results.pose_landmarks:
			# x座標に切り抜いた左側の位置を足し合わす
			vPoints = [(int(landmark.x*imROI.shape[1]+self.leftPosROI), int(landmark.y*imROI.shape[0]))
						for landmark in results.pose_landmarks.landmark]
			blPoseCorrectOnce = judge_pose(
				results.pose_landmarks.landmark, vPoints, self.correctAngles, self.sJudgeMargin)

			self.drawLandamrks(vPoints, 2, (0, 255, 0), 3, (0, 0, 255))

			# ポーズが正解だった時にクラスの判定フラグをTrueにする。また、ここで正解した時間を記録する
			if blPoseCorrectOnce is True:
				self.blPoseCorrect = True
				self.sTimeAtCorrect = time.time()

		# クラスのポーズ判定フラグによって左上に表示する画像を変える
		if self.blPoseCorrect is True:
			self.window.setOverlayImage(self.imOverlayOrig_correct, self.imOverlayMask_correct)
			self.imProcessed = self.imSensor

			# ポーズ判定で正解して３秒以上経過したらクラスのフラグをFalseにし、processの返り値をTrueにする
			if time.time() - self.sTimeAtCorrect >= 2:
				self.blPoseCorrect = False
				return True
		else:
			self.window.setOverlayImage(self.imOverlayOrig_inst, self.imOverlayMask_inst)
			self.imProcessed = self.imSensor

		return 0

if __name__ == '__main__':
	CProc = ClsImageProcessPose
	import os

	if os.name == 'nt':
		strPlatform = 'WIN'
	else:
		strPlatform = 'JETSON'
	
	sCameraNumber = 0
	sSensorWidth = 320
	sSensorHeight = 180
	sMonitorWidth = 1024
	sMonitorHeight = 600
	tplWindowName = ('full',)
	sFlipMode = 1

	proc = CProc(
		strPlatform,
		sCameraNumber,
		sSensorWidth,
		sSensorHeight,
		sMonitorWidth,
		sMonitorHeight,
		tplWindowName,
		sFlipMode)

	proc.createWindows()
	proc.setRatioROI(0.5)
	proc.defineCorrectPose()

	while True:
		proc.execute()
		sKey = cv2.waitKey(1) & 0xFF
		if sKey == ord('q'):
			del proc
			break
