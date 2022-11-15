import numpy as np


def makeListOfAngles(vLandmarks, vPoints):
	vAngles = []

	# 左腕
	vAngles.append(measureAngle(vLandmarks, vPoints, [12, 11, 14]))
	vAngles.append(measureAngle(vLandmarks, vPoints, [14, 12, 16]))
	# 左足
	vAngles.append(measureAngle(vLandmarks, vPoints, [24, 12, 26]))
	vAngles.append(measureAngle(vLandmarks, vPoints, [26, 24, 28]))
	# 右腕
	vAngles.append(measureAngle(vLandmarks, vPoints, [11, 13, 12]))
	vAngles.append(measureAngle(vLandmarks, vPoints, [13, 15, 11]))
	# 右足
	vAngles.append(measureAngle(vLandmarks, vPoints, [23, 11, 25]))
	vAngles.append(measureAngle(vLandmarks, vPoints, [25, 23, 27]))

	return vAngles


def visibilityCheck(vLandmarks, vPointNumbers):
	visibilityThresh = 0.3
	if (vLandmarks[vPointNumbers[0]].visibility > visibilityThresh 
	and vLandmarks[vPointNumbers[1]].visibility > visibilityThresh
	and vLandmarks[vPointNumbers[2]].visibility > visibilityThresh):
		return True
	else:
		return False

# aを中心とする角度
def measureAngle(vLandmarks, vPoints, vPointNumbers):
	if visibilityCheck(vLandmarks, vPointNumbers):
		vPostPivot = np.array(vPoints[vPointNumbers[0]])
		vPostAround1 = np.array(vPoints[vPointNumbers[1]])
		vPostAround2 = np.array(vPoints[vPointNumbers[2]])

		if (np.array_equal(vPostPivot, vPostAround1) 
		or np.array_equal(vPostAround1, vPostAround2) 
		or np.array_equal(vPostAround2, vPostPivot)):
			return -1

		if ((vPostPivot[0] >= 0 and vPostPivot[1] >= 0) 
		and (vPostAround1[0] >= 0 and vPostAround1[1] >= 0) 
		and (vPostAround2[0] >= 0 and vPostAround2[1] >= 0)):
			pass
		else:
			return -1

		vec1 = vPostAround1 - vPostPivot
		vec2 = vPostAround2 - vPostPivot
		sNormVec1 = np.linalg.norm(vec1)
		sNormVec2 = np.linalg.norm(vec2)
		sInnerProduct = np.inner(vec1, vec2)
		sCosineDegree = sInnerProduct / (sNormVec1 * sNormVec2)
		sDegree = np.rad2deg(np.arccos(sCosineDegree))

		if np.cross(vec1, vec2) < 0:
			return sDegree
		else:
			return 360 - sDegree

	else:
		return -1


def judge_pose(vLandmarks, vPoints, correctAngles, sJudgeMargin):
	currentAngles = makeListOfAngles(vLandmarks, vPoints)

	flag = True
	for i in range(0, 8):
		if i in (2, 3, 6, 7):
			continue
		if correctAngles[i] - sJudgeMargin  <= currentAngles[i] \
		and currentAngles[i] <= correctAngles[i] + sJudgeMargin:
			pass
		else:
			flag = False

	return flag
