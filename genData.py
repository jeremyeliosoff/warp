#!/usr/bin/python
import pygame, math, ut, os, pprint, sys, random, time, shutil, glob, importlib, subprocess
import fragmod
import cPickle as pickle
# OpenCl stuff!
import pyopencl as cl
import numpy as np
from PIL import Image

import pprint

pp = pprint.PrettyPrinter(indent=4)


outFile = "/tmp/out"



neighboursToConns = {
	# a
	(0, 0,\
	 0, 0):[],
	# b
	(0, 0,\
	 0, 1):[((0, 1), (1, 0))],
	# c
	(0, 0,\
	 1, 0):[((-1, 0), (0, 1))],
	# d
	(0, 0,\
	 1, 1):[((-1, 0), (1, 0))],
	# e
	(0, 1,\
	 0, 0):[((1, 0), (0, -1))],
	# f
	(0, 1,\
	 0, 1):[((0, 1), (0, -1))],
	# g
	(0, 1,\
	 1, 0):[((-1, 0), (0, 1)), ((1, 0), (0, -1))],
	# h
	(0, 1,\
	 1, 1):[((-1, 0), (0, -1))],
	# i
	(1, 0,\
	 0, 0):[((0, -1), (-1, 0))],
	# j
	(1, 0,\
	 0, 1):[((0, 1), (1, 0)), ((0, -1), (-1, 0))],
	# k
	(1, 0,\
	 1, 0):[((0, -1), (0, 1))],
	# l
	(1, 0,\
	 1, 1):[((0, -1), (1, 0))],
	# m
	(1, 1,\
	 0, 0):[((1, 0), (-1, 0))],
	# n
	(1, 1,\
	 0, 1):[((0, 1), (-1, 0))],
	# o
	(1, 1,\
	 1, 0):[((1, 0), (0, 1))],
	# p
	(1, 1,\
	 1, 1):[]}

class curve:
	inSurf = False
	surf = None
	surfDic = None
	head = None
	tail = None
	nJoints = 0
	cid = None
	level = None
	avgTexClr = None
	avgXy = None
	bbx = None
	prevCids = {}

	def add(self, jt):
		jt.pv = self.head
		if self.head:
			self.head.nx = jt
		self.head = jt
		self.level = jt.level
		self.bbx = bbxAccom(self.bbx, jt.xy)

	def __init__(self, jt, nCurves, inSurf):
		self.inSurf = inSurf
		self.tail = jt
		self.bbx = [list(jt.xy), list(jt.xy)]
		self.add(jt)
		self.cid = nCurves

class joint:
	xy = None
	level = None
	cons = None
	nx = None
	pv = None
	cv = None

	def __init__(self, xy, level, cons):
		self.xy = xy
		self.level = level
		self.cons = cons

	def __str__(self):
		return "<joint> xy: " + str(self.xy) + "; level: " + str(self.level) +  \
			"\n\tcons:" + str(self.cons)


class surf:
	inSurf = None # TODO: FFS rename this - outerCurve
	inHoles = []
	sid = None
	tid = None
	level = None
	bbx = None

	def __init__(self, inSurf, sid):
		self.inSurf = inSurf
		self.level = inSurf.level
		self.sid = sid
		self.tid = sid
		self.bbx = inSurf.bbx



# FUNCTIONS

def toClrSpaceCIn255(r, g, b, c255):
	c = vBy255(c255)
	ret = ut.multVSc(r, c[0])
	ret = ut.vAdd(ut.multVSc(g, c[1]), ret)
	ret = ut.vAdd(ut.multVSc(b, c[2]), ret)
	return ret

def toClrSpace(r, g, b, c):
	ret = ut.multVSc(r, c[0])
	ret = ut.vAdd(ut.multVSc(g, c[1]), ret)
	ret = ut.vAdd(ut.multVSc(b, c[2]), ret)
	return ret


def bbxAccom(bbxOld, xy):
	bbxNew = bbxOld
	bbxNew[0][0] = min(bbxNew[0][0], xy[0])
	bbxNew[0][1] = min(bbxNew[0][1], xy[1])
	bbxNew[1][0] = max(bbxNew[1][0], xy[0])
	bbxNew[1][1] = max(bbxNew[1][1], xy[1])
	return bbxNew

def bbxUnion(bbxA, bbxB):
	bbxUnion = [[None for i in range(2)] for j in range(2)]
	for xy in range(2):
		bbxUnion[0][xy] = min(bbxA[0][xy], bbxB[0][xy])
		bbxUnion[1][xy] = max(bbxA[1][xy], bbxB[1][xy])
	return bbxUnion


def pOut(*ss):
	ret = ""
	for s in ss:
		ret += str(s) + " "
	ret += "\n"
	with open(outFile, "a") as f:
		f.write(ret)
	#os.system("echo " + ret + " >> " + outFile)
	return ret

	

	

def pickleDump(filePath, data):
	print "_pickleDump(): filePath", filePath, "..."
	with open(filePath, 'wb') as dataFile:
		pickle.dump(data, dataFile)
	print "_pickleDump(): \tDone pickle dumping", filePath

def pickleLoad(filePath):
	print "_pickleLoad(): Pickle loading", filePath, "..."
	
	if os.path.exists(filePath):
		with open(filePath, 'rb') as dataFile:
			ret = pickle.load(dataFile)
	else:
		print "_pickleLoad() ERROR: file not found!"
		ret = None
	return ret

def border(img, v=(0, 0, 0, 255)):
	res = img.get_size()
	for x in range(res[0]):
		img.set_at((x, 0), v)
		img.set_at((x, res[1]-1), v)

	for y in range(1,res[1]-1):
		img.set_at((0, y), v)
		img.set_at((res[0]-1, y), v)


def avgLs(l):
	tot = 0
	for i in l:
		tot += i
	return float(tot)/len(l)



def vBy255(v):
	ret = [float(f)/255 for f in v]
	if type(v) == type(()):
		ret = tuple(ret)
	return ret

def vX255(v):
	ret = [int(f*255) for f in v]
	if type(v) == type(()):
		ret = tuple(ret)
	return ret


def getLevThresh(warpUi, lev, nLevels):
	minThreshMin = warpUi.parmDic("minThresh")
	maxThreshMax = warpUi.parmDic("maxThresh")
	rangeThresh = warpUi.parmDic("rangeThresh")
	minThreshMax = ut.mix(minThreshMin, maxThreshMax, 1-rangeThresh)
	maxThreshMin = ut.mix(minThreshMin, maxThreshMax, rangeThresh)

	levThresh = warpUi.getOfsWLev(lev) % 1.0
	#levThreshRemap = ut.gamma(levThresh, warpUi.parmDic("gamma"))

	levRel = float(lev)/(nLevels-1)
	minThreshThisLev = ut.mix(minThreshMin, minThreshMax, levRel)
	maxThreshThisLev = ut.mix(maxThreshMin, maxThreshMax, levRel)


	levThreshRemap = levThresh
	levThreshRemap = ut.mix(minThreshThisLev, maxThreshThisLev, levThreshRemap)
	levThreshRemap = ut.gamma(levThreshRemap, warpUi.parmDic("gamma"))
	print "_getLevThresh(): levThresh:", levThresh, ", levThreshRemap:", levThreshRemap
	levThreshInt = int(levThreshRemap*255)
	return levThreshRemap, levThreshInt




def initJtGrid(img, warpUi):
	print "\n_initJtGrid(): BEGIN"
	nLevels = warpUi.parmDic("nLevels")
	res = img.get_size()
	nJoints = 0
	tholds = [None for lev in range(nLevels)]
	
	ut.timerStart(warpUi, "initJtGridXYLoop")

	jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
	jtCalcMode = "plugin"
	if jtCalcMode == "plugin":
		print "XXXXXXXXXXXXxxx AAAAAAA"
		#fragmod.initJtGrid(xres, yres, lev, imgArray, levThreshArray, nconsOut)
		xres,yres = res
		imgArray = np.array(list(pygame.surfarray.array3d(img)), dtype=np.intc)
		# print "YYYYYY imgArray", imgArray
		# print "YYYYYY type", type(imgArray[0][0][0])

		levThreshRemap = []
		levThreshInt = []
		for lev in range(nLevels):
			thisLevThreshRemap, thisLevThreshInt = \
				getLevThresh(warpUi, lev, nLevels)
			levThreshRemap.append(thisLevThreshRemap)
			tholds[lev] = thisLevThreshRemap
			# TODO -> tholds[lev] = thisLevThreshRemap
			levThreshInt.append(thisLevThreshInt)
			print "POST _getLevThresh()"

		print "_initJtGrid(): levThreshInt:", levThreshInt
		print "_initJtGrid(): levThreshRemap:", levThreshRemap
		levThreshArray = np.array(levThreshInt, dtype=np.intc)

		jtCons = np.empty((nLevels, res[0], res[1]), dtype=np.intc)
		jtCons.fill(0)

		for lev in range(nLevels):
			nconsOut = np.empty((res[0], res[1]), dtype=np.intc)
			nconsOut.fill(0)
			dud = fragmod.initJtGrid(xres, yres, lev, imgArray, levThreshArray, nconsOut)
			#print "imgArray", imgArray
			#print "nconsOut", nconsOut
			print "levThreshArray", levThreshArray
			jtCons[lev] = nconsOut

		# TODO Make this into a C function
		for lev in range(nLevels):
			levThreshRemap, levThreshInt = getLevThresh(warpUi, lev, nLevels)
			for x in range(res[0]-1):
				for y in range(res[1]-1):
					jtConsKey = jtCons[lev][x][y]
					# TEMP: below should never be!!
					if jtConsKey >= len(decodeCons) or jtConsKey < 0:
						jtConsKey = 0
					gpuCons = decodeCons[jtConsKey]
					if len(gpuCons) > 0:
						jtLs = []
						for gpuCon in gpuCons:
							jtLs.append(joint((x,y), levThreshRemap, gpuCon))
						jtGrid[x][y][lev] = jtLs

		# Mark clean after GPU ops.
		ut.indicateProjDirtyAs(warpUi, False, "initJtGridGPU_inProgress")
	# Write stats

	renPath = warpUi.images["ren"]["path"]
	renSeqDir = "/".join(renPath.split("/")[:-1]) #TODO: Do this with os.path.
	ut.mkDirSafe(renSeqDir)

	ut.timerStop(warpUi, "initJtGridXYLoop")
	#print "\n\n\nyyyyyyyyJJJJJJJJ jtGrid:"
	#for row in range(len(jtGrid[0])):
	#	s = ""
	#	for clm in range(len(jtGrid)):
	#		dic = jtGrid[clm][row]
	#		if dic == {}:
	#			s += "."
	#		else:
	#			s += str(dic.keys()[0])
	#	print s

	return jtGrid, tholds

def setAovFullImg(warpUi, aovName, img, lev, sfx=""):
	aovParmName = "aov_" + aovName	
	if aovParmName in warpUi.parmDic.parmDic.keys() and warpUi.parmDic(aovParmName) == 1:
		destDir, destPath = warpUi.getDebugDirAndImg(aovName, lev, sfx=sfx)
		ut.mkDirSafe(destDir)
		pygame.image.save(img, destPath)
	else:
		print "_setAovFullImg(): aov doesn't exist or is not on!!", aovName, aovParmName,
		pd = warpUi.parmDic.parmDic.keys()
		pd.sort()
		print pd

def setAovXy(warpUi, name, lev, nLevels, x, y, val):
	aovParmName = "aov_" + name	
	if aovParmName in warpUi.parmDic.parmDic.keys() and warpUi.parmDic(aovParmName) == 1 and lev <= len(warpUi.aovDic[name]): # TODO: Won't last cond always be true?
		res = warpUi.aovDic[name][lev].get_size()
		if x < res[0] and y < res[1]:
			newVal = tuple(list(val))
			newVal = ut.clampVSc(newVal, 0, 255)
			warpUi.aovDic[name][lev].set_at((x,y), newVal)
			warpUi.aovDic[name][nLevels].set_at((x,y), newVal)


def drawBbx(warpUi, bbx, dbName, lev, nLevels, clr):
	# Draw cvBbx
	xmn, ymn = bbx[0]
	xmx, ymx = bbx[1]
	# Vertical lines
	for xx in range(xmn, xmx):
		setAovXy(warpUi, dbName, lev, nLevels, xx, ymn, clr)
		setAovXy(warpUi, dbName, lev, nLevels, xx, ymx, clr)
	# Horizontal lines
	for yy in range(ymn, ymx):
		setAovXy(warpUi, dbName, lev, nLevels, xmn, yy, clr)
		setAovXy(warpUi, dbName, lev, nLevels, xmx, yy, clr)
	
# From neighboursToConns:
decodeCons = ((),
	((( 0,  1), ( 1,  0)),),	# 1
	((( 1,  0), ( 0, -1)),),	# 2
	#((( 1,  0), (-1,  0)),),	# 3
	((( 0,  1), ( 0, -1)),),	# 3
	(((-1,  0), ( 0,  1)),),	# 4
	(((-1,  0), ( 1,  0)),),	# 5
	(((-1,  0), ( 0,  1)), ((1, 0), (0, -1)),),	# 6
	(((-1,  0), ( 0, -1)),),	# 7
	((( 0, -1), (-1,  0)),),	# 8
	((( 0,  1), ( 1,  0)), ((0, -1), (-1, 0)),),	# 9
	((( 1,  0), (-1,  0)),),	# 10
	((( 0,  1), (-1,  0)),),	# 11
	((( 0, -1), ( 0,  1)),),	# 12
	((( 0, -1), ( 1,  0)),),	# 13
	((( 1,  0), ( 0,  1)),),	# 14
	())



encodeCons = {}
for i,cons in enumerate(decodeCons):
	encodeCons[cons] = i

#[
#	()
#	((0, 0), ( 0, 1)),
#	((0, 0), ( 1, 0)),
#	((0, 0), ( 1, 1)),
#	((0, 1), ( 0, 1)),
#	((0, 1), ( 1, 0)),
#	((0, 1), ( 1, 1)),
#	((1, 0), ( 0, 0)),
#	((1, 0), ( 0, 1)),
#	((1, 0), ( 1, 0)),
#	((1, 0), ( 1, 1)),
#	((1, 1), ( 0, 0)),
#	((1, 1), ( 0, 1)),
#	((1, 1), ( 1, 0)),
#	((1, 1), ( 1, 1)),
#	((0, 0), ( 0, 0))]

def loadPrevFrData(warpUi):
	print "_loadPrevFrData BEGIN"
	fr = warpUi.parmDic("fr")
	prevInSurfGridPath = warpUi.framesDataDir + ("/%05d/inSurfGrid" % (fr-1))
	if warpUi.inSurfGridPrev == None:
		if os.path.exists(prevInSurfGridPath):
			print "_loadPrevFrData(): inSurfGridPrev == None and prev one found, loading..."
			warpUi.inSurfGridPrev = pickleLoad(prevInSurfGridPath)
		else:
			print "_loadPrevFrData(): prevInSurfGridPath not found!!", prevInSurfGridPath

	## sidToTid is NOT CURRENTLY USED!!
	#prevSidToTidPath = warpUi.framesDataDir + ("/%05d/sidToTid" % (fr-1))
	#if warpUi.sidToTid == None:
	#	if os.path.exists(prevSidToTidPath):
	#		print "_loadPrevFrData(): sidToTid == None and prev one found, loading..."
	#		warpUi.sidToTid = pickleLoad(prevSidToTidPath)
	#	else:
	#		print "_loadPrevFrData(): prevSidToTidPath not found!!", prevSidToTidPath

	prevMetaDataPath = warpUi.framesDataDir + ("/%05d/metaData" % (fr-1))
	if os.path.exists(prevMetaDataPath):
		print "_loadPrevFrData(): metaData == None and prev one found, loading..."
		metaData = pickleLoad(prevMetaDataPath)
		if "nextSid" in metaData.keys():
			print "_loadPrevFrData(): metaData: setting warpUi.nextSid to", \
				metaData["nextSid"]
			warpUi.nextSid = metaData["nextSid"]
	else:
		print "_loadPrevFrData(): prevMetaDataPath not found!!", prevMetaDataPath

	print "_loadPrevFrData END"


def loadLatestTidToSids(warpUi):
	print "_loadLatestTidToSids(): BEGIN - finding last tidToSidsFile."
	lastFramePath = getLastFrameDirPath(warpUi)
	tidToSidsPath = lastFramePath + "/tidToSids"
	print "_loadLatestTidToSids(): attempting to load", tidToSidsPath, "..."
	if os.path.exists(tidToSidsPath):
		print "_loadLatestTidToSids(): Found, _pickleLoad-ing..."
		warpUi.tidToSids = pickleLoad(tidToSidsPath)
	else:
		print "_loadLatestTidToSids(): Not found, attempting to find last checkpoint..."
		lastFr = int(lastFramePath.split("/")[-1])
		print "_loadLatestTidToSids(): \tlastFr", lastFr
		bde = warpUi.parmDic("backupDataEvery")
		lastCheckpoint = bde*(lastFr/bde)
		print "_loadLatestTidToSids(): \tlastCheckpoint", lastCheckpoint
		lastCheckpointTidToSids = getLastFrameDirPath(warpUi, lastCheckpoint) \
			+ "/tidToSids"
		print "_loadLatestTidToSids(): \tlastCheckpointTidToSids", lastCheckpointTidToSids
		print "_loadLatestTidToSids(): \tChecking existence..."
		if os.path.exists(lastCheckpointTidToSids):
			print "_loadLatestTidToSids(): Found! _pickleLoad-ing..."
			warpUi.tidToSids = pickleLoad(lastCheckpointTidToSids)

		else:
			print "_loadLatestTidToSids(): Not found - I hope you're starting a new data version?  Setting to None."
			warpUi.tidToSids = None

def growCurves(warpUi, jtGrid, frameDir):
	print "\n_growCurves(): growing curves for", frameDir
	nLevels = warpUi.parmDic("nLevels")
	nCurves = 0
	fr = warpUi.parmDic("fr")
	res = (len(jtGrid), len(jtGrid[0]))
	
	if warpUi.tidToSids == None:
		loadLatestTidToSids(warpUi)
		loadPrevFrData(warpUi)
		if warpUi.tidToSids == None:
			warpUi.tidToSids = [{} for i in range(nLevels)]
	#if warpUi.sidToTid == None:
	#	warpUi.sidToTid = [{} for i in range(nLevels)]

	#frDirDebug = open(frameDir + "/debug", 'w')
	#frDirDebug.write("PRE warpUi.nextSid:" + str(warpUi.nextSid) + "\n\n")

	tidToSidsStr = "PRE warpUi.tidToSids:\n"
	ks = warpUi.tidToSids[1].keys()
	ks.sort()
	for k in ks:
		kks = warpUi.tidToSids[1][k].keys()
		kks.sort()
		for kk in kks:
			tidToSidsStr += str(k) + ":" + str(kk) + ":" + str(warpUi.tidToSids[1][k][kk]) + "\n"
		tidToSidsStr += "\n"

	#frDirDebug.write(tidToSidsStr)

	# inHoles delimit holes; inSurfs do not.
	curToPrevSidDic = [{} for i in range(nLevels)]
	surfs = [[] for i in range(nLevels)]
	inHoles = [[] for i in range(nLevels)]
	inSurfs = [[] for i in range(nLevels)]
	inSurfNow = [False for i in range(nLevels)]
	curves = [[] for i in range(nLevels)]
	#sidToCurves = [{}] * nLevels

	inSurfGrid = [[[None for yy in range(res[1])] for xx in range(res[0])] for lev in range(nLevels)] # inSurfGridASSIGN!



	# Grow curves following the con(nection)s in _jtGrid

	ut.timerStart(warpUi, "growC_xyloop")
	nextPrintout = 10
	for y in range(res[1]):
		pct = int(100*float(y)/res[1])
		if pct >= nextPrintout:
			print "_growCurves(): %d%%" % pct # in place didn't update enough: print "Progress %d%%\r" % pct,
			nextPrintout += 10
		for x in range(res[0]):
			# Initiate curve growth for any joints in this cell of _jtGrid.

			# GPUtrans _jtGrid (effectively) becomes jtCons - maybe list, not dic
			ut.timerStart(warpUi, "growC_curves")
			#print "\niii x=", x, "y=", y
			for lev,jts in jtGrid[x][y].items():
				#print "hhh lev", lev, "jts", jts
				for jt in jts:
					# GPUtrans: I think this can become "if cvGrid[x][y][lev] == None"
					if jt.cv == None:
						# GPUtrans: cvGrid[x][y][lev] = curve(...)
						jt.cv = curve(jt, nCurves, inSurfNow[lev])
						nCurves += 1
						xx = x + jt.cons[1][0]
						yy = y + jt.cons[1][1]
						#print "ggggggggggg jtGrid[", xx, "][", yy, "][", lev, "]=", jtGrid[xx][yy][lev]
						#print "ggggggggggg lev=", lev, "jtGrid[", xx, "][", yy, "]=", jtGrid[xx][yy]
						for jtt in jtGrid[xx][yy][lev]:
							# GPUtrans: [1][0] may become [2], etc.
							#print "jtt.cons", jtt.cons
							#print "jt.cons", jt.cons
							#print "jtt.cons[0][0]", jtt.cons[0][0],  "-jtt.cons[1][0]", -jtt.cons[1][0]
							#print "jtt.cons[0][1]", jtt.cons[0][1], "-jtt.cons[1][1]", -jtt.cons[1][1]
							#print jtt.cons[0][0] == -jt.cons[1][0] 
							#print jtt.cons[0][1] == -jt.cons[1][1]
							if jtt.cons[0][0] == -jt.cons[1][0] and jtt.cons[0][1] == -jt.cons[1][1]:
								#print "YES"
								thisJt = jtt
						nJoints = 0
						xTot = 0
						yTot = 0
						
						# Grow the actual curve.
						cvClr = ut.intToClr(jt.cv.cid)
						while thisJt.cv == None:
							xTot += xx
							yTot += yy
							nJoints += 1
							setAovXy(warpUi, "cid", lev, nLevels, xx, yy, cvClr)
							thisJt.cv = jt.cv
							#print "adding xx", xx, "yy", yy
							jt.cv.add(thisJt)
							xx += thisJt.cons[1][0]
							yy += thisJt.cons[1][1]

							for jtt in jtGrid[xx][yy][lev]:
								if jtt.cons[0][0] == -thisJt.cons[1][0] and  jtt.cons[0][1] == -thisJt.cons[1][1]:
									thisJt = jtt
						jt.cv.nJoints = nJoints
						#jt.cv.avgXy = (float(xx)/nJoints, float(xx)/nJoints)
						curves[lev] = curves[lev][:] + [jt.cv]


					# Register when entering or leaving a curve.  By convention, only look at y = -1 direction.

					if jt.cons[0][1] == -1 or jt.cons[1][1] == -1:

						inSurfNow[lev] = not inSurfNow[lev]
						# NOTE: inHoles and _inSurfs are arrays because you can be inside multiple 
						# surfs and mutiple holes at once.
						if inSurfNow[lev]:
							#Case 1: closing hole
							if len(inHoles[lev]) > 0 and inHoles[lev][-1] == jt.cv:
								inHoles[lev].pop()
							#Case 2: this is a new inSurf
							else:
								if jt.cv.surf == None:
									thisSurf = surf(jt.cv, warpUi.nextSid)
									surfs[lev] = surfs[lev][:] + [thisSurf] #TODO: this could probably be append
									jt.cv.surf = thisSurf
									thisSurfDic = {"inSurf": jt.cv, "sid": warpUi.nextSid, "inHoles": []}
									jt.cv.surfDic = thisSurfDic
									warpUi.nextSid += 1
								if not jt.cv in inSurfs[lev]: # TODO: this could be a set?
									inSurfs[lev] = inSurfs[lev][:] + [jt.cv]
						else:
							#Case 3: closing inSurf
							if len(inSurfs[lev]) > 0 and inSurfs[lev][-1] == jt.cv:
								inSurfs[lev] = inSurfs[lev][:-1]
							#Case 4: this is a new hole
							else:
								#if not jt.cv in inSurfs[lev][-1].surf.inHoles:
								if not jt.cv in inSurfs[lev][-1].surfDic["inHoles"]:
									inSurfs[lev][-1].surf.inHoles = inSurfs[lev][-1].surf.inHoles[:] + [jt.cv]
									inSurfs[lev][-1].surfDic["inHoles"] = inSurfs[lev][-1].surfDic["inHoles"][:] + [jt.cv]
								jt.cv.surf = inSurfs[lev][-1].surf
								inHoles[lev] = inHoles[lev][:] + [jt.cv]
			ut.timerStop(warpUi, "growC_curves")
			# -- END OF for lev,jts in jtGrid[x][y].items():

			
			# Work out which prev surf the cur surfs are in.

			for lev in range(nLevels):
				if inSurfNow[lev]:
					currentSid = inSurfs[lev][-1].surf.sid
					inSurfGrid[lev][x][y] = currentSid # inSurfGridASSIGN!
					if not (warpUi.inSurfGridPrev == None or
						# I THINK below avoids overlapping start of cyc with end of prev
						(not math.floor(warpUi.getOfsWLev(lev)) ==
							math.floor(warpUi.getOfsWLev(lev, fr-1)))) : # NOTE:  this is apparently NOT the same as "if warpUi.inSurfGridPrev:"
						# There is a surfGrid file for the previous frame.
						#print "nnnnnnn lev", lev, "x,y", x, y
						inSurfPrev = warpUi.inSurfGridPrev[lev][x][y]
						if inSurfPrev == None:
							# There are NO surfs at this level at this pxl in the previous frame.
							if not currentSid in curToPrevSidDic[lev].keys():

								# There are no prev sids corresponding to the current sid.
								# If there's nothing in the prev frame here and you haven't
								# recorded anything in curToPrevSidDic, record an empty list.
								# TODO: Do you really need above conditional?  Just repeately re-set it?
								# MAYBE TRY A *SET*!
								#curToPrevSidDic[lev][currentSid] = []
								curToPrevSidDic[lev][currentSid] = set([])
						else:
							# There ARE surfs in this pxl in the previous frame.
							if currentSid in curToPrevSidDic[lev].keys():
								# There is already a dict for currentSid in
								# curToPrevSidDic
								if not inSurfPrev in curToPrevSidDic[lev][currentSid]:
									# ...which doesn't' include inSurfPrev; append it
									# ie. JOIN inSurfPrev to currentSid
									#curToPrevSidDic[lev][currentSid].append(inSurfPrev)
									curToPrevSidDic[lev][currentSid].add(inSurfPrev)
							else:
								# There's no list for currentSid,
								# make a new one with just inSurfPrev
								curToPrevSidDic[lev][currentSid] = {inSurfPrev}
	
	#inSurfGridStr = "MID inSurfGrid:\n"	
	#for y in range(res[1]):
	#	for x in range(res[0]):
	#		inSurfGridStr += str(inSurfGrid[1][x][y]) + " "
	#	inSurfGridStr += "\n"
	#inSurfGridStr += "\n\n"
	#frDirDebug.write(inSurfGridStr)

	#ut.timerStop(warpUi, "growC_surfs")

	ut.timerStop(warpUi, "growC_xyloop")

	# Draw the curve joint to joint - I think this is just for debug.

	ut.timerStart(warpUi, "growC_aovs")
	sidToCvs = [{} for i in range(nLevels)]
	sidToSurf = [{} for i in range(nLevels)]
	cidToCurve = [{} for i in range(nLevels)]
	for lev in range(nLevels):
		for cv in curves[lev]:
			cidToCurve[lev][cv.cid] = cv
			sid = cv.surf.sid
			if sid in sidToCvs[lev].keys():
				sidToCvs[lev][sid]["cvs"].append(cv)
				sidToCvs[lev][sid]["bbx"] = bbxUnion(sidToCvs[lev][sid]["bbx"], cv.surf.bbx)
			else:
				# TODO: looks like you're comparing each curve's bbx - should only be done with inSurfs
				sidToCvs[lev][sid] = {"cvs":[cv], "bbx":cv.surf.bbx}

			# TODO: next line - I thought a sid could have > 1 surfs??? It appears surf is never used, just key.
			sidToSurf[lev][sid] = cv.surf
			jt = cv.head
			sfClr = ut.intToClr(jt.cv.surf.sid)
			while True:
				xx, yy = jt.xy
				setAovXy(warpUi, "cvSid", lev, nLevels, xx, yy, sfClr)
				sfClr = ut.intToClr(jt.cv.cid)
				setAovXy(warpUi, "cidPost", lev, nLevels, xx, yy, sfClr)
				jt = jt.pv
				if jt == None:
					break

			# Draw cvBbx
			drawBbx(warpUi, cv.bbx, "cidPost", lev, nLevels, sfClr)
	ut.timerStop(warpUi, "growC_aovs")


	# Sort out which sids need to be merged (and eventually split):
	#   merge: multiple prev surfs overlap a given cur surf
	#   split: multiple cur surfs overlap a given prev surf
	# At the moment, definitions + concepts have limited clarity + utility.
	# One sid applies to >= 1 surf at this fr, ie. all the surfs that splitted
	# from a "common ancestor", but with no regard to future merging.
	
	# Eventually, there will be the concept of a "branch", ie:
	# the sequence of contiguuous surfs between a "root" (start, no prev surf) or
	# split, and the next merge or "tip" (end, no next surf)
	# A branch has exactly 1 surf per frame for all the frames within a range.
	# A "turf" (tid, time-surf) consists of >= 1 branch, connected by splits
	# and/or merges.

	ut.timerStart(warpUi, "growC_findToMerge")

	mergeKeySidToValSid = [{} for i in range(nLevels)]
	births = [[] for i in range(nLevels)] # NOT YET USED
	sidOldToNew = [{} for i in range(nLevels)]
	allPrevs = [[] for i in range(nLevels)]
	for lev in range(nLevels):
		for sidOld,prevs in curToPrevSidDic[lev].items():
			if len(prevs) == 0:
				births[lev].append(sidOld) # NOT YET USED
			else:
				prevsLs = list(prevs)
				prevsLs.sort()
				sidNew = prevsLs[0]
				if sidOld in allPrevs[lev] and sidNew in sidToCvs[lev].keys():
					# Another sid has the same prev, ie. this is a SPLIT.
					sidToCvs[lev][sidNew]["cvs"] += sidToCvs[lev][sidOld]["cvs"][:] # TODO: why [:]?
					sidToCvs[lev][sidNew]["bbx"] = bbxUnion(sidToCvs[lev][sidNew]["bbx"], sidToCvs[lev][sidOld]["bbx"])
					
				allPrevs[lev] += prevsLs
				if len(prevs) > 1:
					# Register the merge; elements after the first will merge to the first.
					for prev in prevsLs[1:]:
						mergeKeySidToValSid[lev][prev] = sidNew
				if sidNew in curToPrevSidDic[lev].keys():
					# TODO: Avoid this by assigning new sids based on largest sid
					# in prev frame, ie. keep track of nSurfs accross frames.
					print "\n_growCurves(): ---------ERROR, sid already exists! sidNew=", sidNew, "_curToPrevSidDic[lev][sidNew]:", curToPrevSidDic[lev][sidNew]
					continue
				if not sidNew == sidOld:
					# Splitting: add sidOld's cv's to sidNew, then delete sidOld.
					if sidNew in sidToCvs[lev].keys():
						sidToCvs[lev][sidNew]["cvs"] += sidToCvs[lev][sidOld]["cvs"]
						sidToCvs[lev][sidNew]["bbx"] = bbxUnion(sidToCvs[lev][sidNew]["bbx"], sidToCvs[lev][sidOld]["bbx"])
					else:
						sidToCvs[lev][sidNew] = sidToCvs[lev][sidOld]
					del(sidToCvs[lev][sidOld])
					sidToSurf[lev][sidNew] = sidToSurf[lev][sidOld]
					del(sidToSurf[lev][sidOld])
					sidOldToNew[lev][sidOld] = sidNew

	ut.timerStop(warpUi, "growC_findToMerge")



	# Merge surfaces for marked sids.

	ut.timerStart(warpUi, "growC_doMerge")
	for lev in range(nLevels):
		print "_growCurves(): lev:", lev, "sids to be merged:", mergeKeySidToValSid[lev].keys()
		# Merge branches.
		for sid in set(allPrevs[lev] + sidToSurf[lev].keys()):
			if sid in mergeKeySidToValSid[lev].keys():
				# This sid will be merged.
				sidToMergeTo = mergeKeySidToValSid[lev][sid]
				if sidToMergeTo in warpUi.tidToSids[lev].keys():
					warpUi.tidToSids[lev][sidToMergeTo]["sids"].add(sid)
				else:
					warpUi.tidToSids[lev][sidToMergeTo] = \
						{"birthFr": fr, "sids":set([sid])}
				if sid in sidToCvs[lev].keys():
					#cvsToAdd = sidToCvs[lev][sid]["cvs"]
					if sidToMergeTo in sidToCvs[lev].keys():
						# Combine cvs - TODO might ren faster if curves kept separate
						sidToCvs[lev][sidToMergeTo]["cvs"] += sidToCvs[lev][sid]["cvs"]
						sidToCvs[lev][sidToMergeTo]["bbx"] = bbxUnion(sidToCvs[lev][sid]["bbx"], sidToCvs[lev][sidToMergeTo]["bbx"])
					else:
						sidToCvs[lev][sidToMergeTo] = sidToCvs[lev][sid]

				# having merged the sid branch, delete it.
				if sid in warpUi.tidToSids[lev].keys():
					print "_growCurves():\t\tdeleting from tidToSids, sid=", sid
					del(warpUi.tidToSids[lev][sid])
				if sid in sidToCvs[lev].keys():
					print "_growCurves():\t\tdeleting from sidToCvs, sid=", sid
					del(sidToCvs[lev][sid])
			elif True: # TODO remove thisnot sid in warpUi.sidToTid[lev].keys(): # Make sure this sid isn't already in a tid.
				# This sid will not be merged, it will be a tid.
				if sid in warpUi.tidToSids[lev].keys():
					warpUi.tidToSids[lev][sid]["sids"].add(sid)
				else:
					warpUi.tidToSids[lev][sid] = \
						{"birthFr" : fr, "sids" : set([sid])}

		# Translate tidToSids to sidToTid.
		# TODO: Is this really what this does?
		# TODO: When you do checkpointing, this is where you del tids > frPerCycle old

		for tid,sidData in warpUi.tidToSids[lev].items():
			# Delete old tids.
			if warpUi.tidToSids[lev][tid]["birthFr"] < fr - 1 \
					- 2*warpUi.parmDic("frPerCycle") - warpUi.parmDic("backupDataEvery"):
				del(warpUi.tidToSids[lev][tid])
				continue
			sids = sidData["sids"]
			sidsThisFr = sidToCvs[lev].keys()
			#if not "bbx" in warpUi.tidToSids[lev][tid].keys() and len(sidData["sids"]) > 0:
			#	# If this tid does not yet have a bbx, initiate it with first surf bbx.
			#	warpUi.tidToSids[lev][tid]["bbx"] = sidToCvs[lev][sidsThisFr[0]]["bbx"]
			#	sidsThisFr = sidsThisFr[1:] # Remove first bbx since you've already added it.
			for sid in sidsThisFr:
				if sid in sids:
					if "bbx" in warpUi.tidToSids[lev][tid].keys():
						warpUi.tidToSids[lev][tid]["bbx"] = bbxUnion(warpUi.tidToSids[lev][tid]["bbx"], sidToCvs[lev][sid]["bbx"])
					else:
						warpUi.tidToSids[lev][tid]["bbx"] = sidToCvs[lev][sid]["bbx"]



			sidToCvsKeys = sidToCvs[lev].keys()
			if len(sidToCvsKeys) > 0:
				firstCurves = sidToCvs[lev][sidToCvsKeys[0]]["cvs"]
				firstCurve = firstCurves[0]

				# TODO: Not convinced this is necessary -- ww reset level a few lines down.
				warpUi.tidToSids[lev][tid]["level"] = firstCurve.level

	ut.timerStop(warpUi, "growC_doMerge")


	print "_growCurves(): updating sids to merged..."
	ut.timerStart(warpUi, "growC_save")
	for lev in range(nLevels):
		for y in range(res[1]):
			for x in range(res[0]):
				sidOld = inSurfGrid[lev][x][y]
				if not sidOld == None:
					if lev <= (len(sidOldToNew) + 1) and sidOld in sidOldToNew[lev].keys():
						sidNew = sidOldToNew[lev][sidOld]
						inSurfGrid[lev][x][y] = sidNew # inSurfGridASSIGN!
					else:
						sidNew = sidOld
	
	drawSidPost = False
	if drawSidPost:
		# Set sidPost AOV using GPU
		print "_growCurves(): drawing sidPost AOV using GPU..."
		# Mark dirty before GPU ops in case of crash.
		ut.indicateProjDirtyAs(warpUi, True, "saveSidPostGPU_inProgress")
		
		kernel = """
	void setArrayCell(int x, int y, int xres,
	  uchar* val,
	  __global uchar* ret)
	{
		int i = y * xres * 3 + x * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}

	int getCellScalar(int x, int y, int xres,
	  __global int* _inSurfGrid)
	{
		int i = y * xres + x;
		return _inSurfGrid[i];
	}

	__kernel void setSidPostAr(
				int xres,
				int nClrs,
				__global int* _inSurfGrid,
				__global uchar* clrsInt,
				__global uchar* sidPostThisAr,
				__global uchar* sidPostALL)
	{
		int x = get_global_id(1);
		int y = get_global_id(0);

		int sid = getCellScalar(x, y, xres, _inSurfGrid);
		//int val = (sid % 2)*255;
		//uchar val = sid > -1 ? (uchar) (100 + 35 * (sid % 4)) : 0;
		//uchar val = sid > -1 ? (uchar) sid : 0;
		int clrInd = sid % nClrs;
		uchar val[] = {0, 0, 0};
		if (sid > -1) {
			val[0] = clrsInt[clrInd * 3];
			val[1] = clrsInt[clrInd * 3+1];
			val[2] = clrsInt[clrInd * 3+2];
			setArrayCell(x, y, xres, val, sidPostALL);
			setArrayCell(x, y, xres, val, sidPostThisAr);
		} else {
			// Strange: if you don't do this, it accumulates levs.
			setArrayCell(x, y, xres, val, sidPostThisAr);
		}
	}
	"""



		sidPostImgs = []

		for lev in range(nLevels):

			inSurfGridNoNone = [[-1 if inSurfGrid[lev][xx][yy] == None else inSurfGrid[lev][xx][yy] for yy in range(res[1])] for xx in range(res[0])]
			#inSurfGridAr = np.array(inSurfGridNoNone[lev], dtype=np.intc)
			inSurfGridAr = np.array(inSurfGridNoNone, dtype=np.intc)
			inSurfGridAr_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.READ_ONLY |
				cl.mem_flags.COPY_HOST_PTR,hostbuf=inSurfGridAr)

			if lev == 0:
				sidPostALL = np.zeros(inSurfGridAr.shape + (3,), dtype=np.uint8)
				sidPostALL_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY |
					cl.mem_flags.COPY_HOST_PTR,hostbuf=sidPostALL)

			clrsIntAr = np.array(ut.clrsInt, dtype=np.uint8)
			clrsIntAr_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.READ_ONLY |
				cl.mem_flags.COPY_HOST_PTR,hostbuf=clrsIntAr)

			sidPostThisLev = np.zeros(inSurfGridAr.shape + (3,), dtype=np.uint8)
			sidPostThisLev_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY,
				sidPostThisLev.nbytes)

			bld = cl.Program(warpUi.cntxt, kernel).build()
			launch = bld.setSidPostAr(
					warpUi.queue,
					inSurfGridAr.shape,
					None,
					np.int32(res[1]),
					np.int32(len(ut.clrsInt)),
					inSurfGridAr_buf,
					clrsIntAr_buf,
					sidPostThisLev_buf,
					sidPostALL_buf)
			launch.wait()

			cl.enqueue_read_buffer(warpUi.queue, sidPostThisLev_buf, sidPostThisLev).wait()
			cl.enqueue_read_buffer(warpUi.queue, sidPostALL_buf, sidPostALL).wait()

			sidPostImgs.append(Image.fromarray(np.swapaxes(sidPostThisLev, 0, 1), 'RGB'))
			#sidPostImgs[lev].save("/tmp/img." + str(lev) + ".png")
		sidPostImgs.append(Image.fromarray(np.swapaxes(sidPostALL, 0, 1), 'RGB'))

		# Mark clean after GPU ops.
		ut.indicateProjDirtyAs(warpUi, False, "saveSidPostGPU_inProgress")

		for lev in range(nLevels + 1):
			levStr = "ALL" if lev == nLevels else "lev%02d" % lev
			levDir,imgPath = warpUi.getDebugDirAndImg("sidPost", levStr)
			ut.mkDirSafe(levDir)
			print "\n\n\n IIIIIIIIIIIIIIIIIIIIII_growCurves(): saving", imgPath
			sidPostImgs[lev].save(imgPath)


	# Save db image with new sids.
	print "_growCurves(): Saving debug images", warpUi.aovDic.keys()
	for aovName,imgs in warpUi.aovDic.items():
		if not aovName == "sidPost":
			for lev in range(nLevels+1):
				levStr = "ALL" if lev == nLevels else "lev%02d" % lev
				levDir,imgPath = warpUi.getDebugDirAndImg(aovName, levStr)
				ut.mkDirSafe(levDir)
				pygame.image.save(imgs[lev], imgPath)

	ut.timerStop(warpUi, "growC_save")
	return inSurfGrid, sidToCvs

	#-- END OF _growCurves(warpUi, jtGrid, frameDir):



def genDataWrapper(warpUi):
	genDataStartTime = time.time()

	img = pygame.image.load(warpUi.images["source"]["path"])
	border(img)

	# Make required dirs.
	fr, frameDir = warpUi.makeFramesDataDir()

	jtGrid, tholds = initJtGrid(img, warpUi)

	ut.timerStart(warpUi, "_growCurves")
	inSurfGrid, sidToCvs = growCurves(warpUi, jtGrid, frameDir)
	ut.timerStop(warpUi, "_growCurves")


	# Save inSurfGrid
	pickleDump(frameDir + "/inSurfGrid", inSurfGrid)
	sidToCvDic = convertCvDicToDic(sidToCvs, warpUi)
	#pickleDump(frameDir + "/sidToTid", warpUi.sidToTid)
	pickleDump(frameDir + "/sidToCvDic", sidToCvDic)
	pickleDump(frameDir + "/tholds", tholds)
	
	metaData = {"nextSid": warpUi.nextSid}
	pickleDump(frameDir + "/metaData", metaData)

	# Save tidToSids every backupDataEvery frames
	if fr % warpUi.parmDic("backupDataEvery") == 0:
		#print "_genData(): BACKING UP tidToSids and sidToTid:"
		print "_genData(): BACKING UP tidToSids :"
		saveTidToSid(warpUi)

	warpUi.inSurfGridPrev = inSurfGrid[:]

	# Record stats
	genDataStopTime = time.time() - genDataStartTime
	memUsage = ut.recordMemUsage(frameDir + "/memUsage")

	statStr = "Time: %.2f seconds\nMemory: %.2f%%\n" % (genDataStopTime, memUsage)
	with open(frameDir + "/stats", 'w') as f:
		f.write(statStr)


def saveTidToSid(warpUi):
	frameDir = getLastFrameDirPath(warpUi)
	picklingIndicator = "pickleInProgress_%05d" % warpUi.parmDic("fr")
	ut.indicateProjDirtyAs(warpUi, True, picklingIndicator)
	pickleDump(frameDir + "/tidToSids", warpUi.tidToSids)
	ut.indicateProjDirtyAs(warpUi, False, picklingIndicator)


def genData(warpUi, statsDirDest):
	ut.timerStart(warpUi, "genData")
	print "\n\n\n"
	print "_genData(): #####################"
	print "_genData(): ### DOING genData ###"
	print "_genData(): #####################"
	print "_genData(): fr:", warpUi.parmDic("fr"), "\n" 
	#renBg(warpUi)  

	if warpUi.genRen1fr == 1:
		genDataWrapper(warpUi)
		renWrapper(warpUi)
		saveTidToSid(warpUi)
	elif warpUi.parmDic("doRenCv") == 1:
		renWrapper(warpUi)
	else:
		genDataWrapper(warpUi)

	#warpUi.cntxt.release()
	#cl.enqueue_release_gl_objects(warpUi.queue)
	ut.timerStop(warpUi, "genData")

def convertCvToLs(cv):
	ret = []
	jt = cv.head
	while True:
		ret.append(jt.xy)
		jt = jt.pv
		if jt == None:
			break
	return ret

def convertCvDicToDic(cvDic, warpUi):
	print "\n_convertCvDicToDic: BEGIN"
	nLevels = warpUi.parmDic("nLevels")
	ret = {} # Could be list instead of dic
	for lev in range(nLevels):
		surfDic = cvDic[lev]
		ret[lev] = {} # To be filed with surf dics.
		for sid,sidData in surfDic.items():
			ret[lev][sid] = {}
			for k,v in sidData.items():
				if k == "cvs":
					cvLs = []
					for cv in v:
						cvLs.append(convertCvToLs(cv))
					ret[lev][sid]["cvs"] = cvLs
				else:
					ret[lev][sid][k] = v

	print "\n_convertCvDicToDic: END"
	return ret
	#sidToCvs[lev][sid].append(cv)

def getLastFrameDirPath(warpUi, fr=None):
	framesDir = warpUi.seqDataVDir + "/frames"
	if fr == None:
		#frameDirs = os.listdir(warpUi.framesDataDir)
		frameDirs = glob.glob(warpUi.framesDataDir + "/[0-9][0-9][0-9][0-9][0-9]")
		frameDirs.sort()
		if len(frameDirs) == 0:
			dud, frameDir = warpUi.makeFramesDataDir()
		else:
			frameDir = frameDirs[-1]
	else:
		frameDir = warpUi.framesDataDir + ("/%05d" % fr)
	return frameDir


###########################
#### REN SPRITES STUFF ####
###########################

def convertTidToClr(tid):
	if tid < 0:
		return (0, 0, 0)
	else:
		if tid == 0: tid = 21111 # Get rid of white, it doesn't tint nicely.
		octant = tid%8
		tDiv = tid/8
		ocR = tDiv % 128 + 128*(octant % 2)
		tDiv = tDiv/128
		ocG = tDiv % 128 + 128*(octant/2 % 2)
		tDiv = tDiv/128
		ocB = tDiv % 128 + 128*(octant/4 % 2)# This should never loop - till we get to tid = 256^3
		return (255-ocR, 255-ocG, 255-ocB)



def converTidPosGridToTidClrGrid(tidPosGrid, tids):
	xres = len(tidPosGrid)
	yres = len(tidPosGrid[0])
	tidClrGrid = np.zeros((xres, yres) + (3,), dtype=np.uint8)
	
	for x in range(xres):
		for y in range(yres): 
			tidPos = tidPosGrid[x][y]
			if tidPos == -1: # TODO: This should never be.
				tidClrGrid[x][y] = (255, 0, 0)
			elif tidPos < len(tids):
				#print "tidPos", tidPos, "len(tids)", len(tids)
				tid = tids[tidPos]
				tidClrGrid[x][y] = convertTidToClr(tidPos)
			else: # TODO: This should never be.
				tidClrGrid[x][y] = (0, 255, 0)
	
	return tidClrGrid



def vecTo3dArray(v, xres, yres):
	ret = np.repeat([v[:]], yres, 0)
	return np.repeat([ret[:]], xres, 0)

#for fr in range(1,6):
#	for lev in range(4):



def invert255(v):
	return 255-v

invert255V = np.vectorize(invert255)

def mult255(v, k):
	return v * k

mult255V = np.vectorize(mult255)





def makeBufferInput(warpUi, inputList, dtype=None):
	if dtype == None:
		ar = np.array(inputList)
	else:
		ar = np.array(inputList, dtype=dtype)
	return cl.Buffer(warpUi.cntxt, cl.mem_flags.READ_ONLY |

		cl.mem_flags.COPY_HOST_PTR,hostbuf=ar)


def makeBufferOutput(warpUi, shape, dtype=None):
	if dtype:
		img = np.zeros(shape, dtype=dtype)
	else:
		img = np.zeros(shape, dtype=np.intc)
	buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=img)
	return img, buf
	

def imgToCspace(warpUi, srcImg, srcImgPath, frIn=None, inOutBoth=2):
	fr = frIn
	if fr == None:
		fr = warpUi.parmDic("fr")
	res = srcImg.get_size()
	srcImgAr = imageToArray3d(srcImg, srcImgPath)

	csImgAr = np.zeros(srcImgAr.shape, dtype=np.intc)
	aovRipAr = np.zeros(srcImgAr.shape, dtype=np.intc)
	cInOutVals = np.array(warpUi.cInOutVals, dtype=np.float32)

	dud,inhFrames = zip(*warpUi.inhParms)
	dud,exhFrames = zip(*warpUi.exhParms)
	brFrames = []
	for i in range(len(inhFrames)):
		brFrames.append(inhFrames[i])
		brFrames.append(exhFrames[i])
	
	ret = fragmod.cspaceImg(cInOutVals, srcImgAr, csImgAr, aovRipAr, np.array(brFrames, dtype=np.intc),
		res[0], res[1], fr, warpUi.parmDic("radiateTime"), inOutBoth, 1)

	csImg = pygame.surfarray.make_surface(csImgAr) 
	aovRipImg = pygame.surfarray.make_surface(aovRipAr) 

	return csImg, aovRipImg
	
def renBg(warpUi): # NOTE: This is not currently used!!
	print "\n_renClrTest(): BEGIN\n"
	#tripFrK = getTripFrK(warpUi)
	#print "\nJJJJJJJJJJJ getTripFrK->", tripFrK
	srcImgPath = warpUi.images["source"]["path"]

	srcImg = pygame.image.load(srcImgPath)
	#srcImg.fill((255, 0, 255), None, pygame.BLEND_MULT)
	# TODO integrate CLR into AOV system
	#destDir = warpUi.seqRenVDir + "/CLR"

	fr = warpUi.parmDic("fr")
	#destPath = destDir + ("/CLR.%05d.png" % fr)


	print "\n_renBg():processing image", srcImgPath, "...."
	csImg, aovRipImg = imgToCspace(warpUi, srcImg, srcImgPath)
	setAovFullImg(warpUi, "bg", csImg, -1, sfx="_ctest")

	#aovRipAr = np.zeros(srcImg.get_size() + (3,), dtype=np.intc)
	#aovRipImg = pygame.surfarray.make_surface(aovRipAr)
	setAovFullImg(warpUi, "rip", aovRipImg, -1, sfx="_ctest")

	# Refresh menus.
	# col = 0
	# for aovName in warpUi.getDbImgParmNames():
	# 	warpUi.updateRenderedAovMenu(warpUi.dbMenus[aovName]["menu"], col)
	# 	col += 1


	print "\n_renBg(): END\n"


def imageToArray3d(srcImg, srcImgPath):
	res = srcImg.get_size()
	info = subprocess.check_output(["identify", srcImgPath]).split(" ")
	if info[6] == "2c": # This means it's a black image, can't use pixels3d
		srcImgAr = np.zeros((res + (3,)), dtype=np.intc)
	else:
		#srcImgAr = pygame.surfarray.array3d(srcImg)
		srcImgAr = pygame.surfarray.pixels3d(srcImg)
	return srcImgAr


def shadeImg(warpUi, bgMode, lev, srcImg, tidPosGridThisLev,
		tids, bbxs, xfs, tidTrips, tripFrK, isBulbs, shadedImgXf):

	# Inputs
	shape2d = (len(tidPosGridThisLev), len(tidPosGridThisLev[0]))
		
	srcImgPath = warpUi.images["source"]["path"]

	srcImgAr = imageToArray3d(srcImg, srcImgPath)

	dud,inhFrames = zip(*warpUi.inhParms)
	dud,exhFrames = zip(*warpUi.exhParms)
	brFrames = []
	for i in range(len(inhFrames)):
		brFrames.append(inhFrames[i])
		brFrames.append(exhFrames[i])

	inhFrames_buf = makeBufferInput(warpUi, inhFrames, dtype=np.intc)
	exhFrames_buf = makeBufferInput(warpUi, exhFrames, dtype=np.intc)
	brFrames_buf = makeBufferInput(warpUi, brFrames, dtype=np.intc)

	# Outputs
	#shadedImg = np.zeros((len(tidImgLs), len(tidImgLs[0]), len(tidImgLs[0][0])), dtype=np.intc)
	#shadedImg_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY |
	#	cl.mem_flags.COPY_HOST_PTR,hostbuf=shadedImg)
	shape3d = shape2d + (3,)
	#shape2d = tidImg.get_size()
	shadedImg, dud = makeBufferOutput(warpUi, shape3d)
	aovRipImg, dud = makeBufferOutput(warpUi, shape3d)
	alphaBoostImg, dud = makeBufferOutput(warpUi, shape2d)

	kRip = ut.mix(.1, 1, tripFrK);

	ofs = warpUi.getOfsWLev(lev) % 1.0
	nLevels = warpUi.parmDic("nLevels")
	levPct = (lev+ofs)/nLevels #int((warpUi.getOfsWLev(lev)*100.0)%100)
	frOfsPerLev = 1
	frLevOfs = (nLevels - 1 - lev) * frOfsPerLev
	fr = warpUi.parmDic("fr")
	frWOfs = fr + frLevOfs + warpUi.parmDic("clrFrOfs")
	#print "\n"*10, "kkkkkkkkkkk bbxs", bbxs
	test = np.array([33,44,55], dtype=np.intc)
	#print "\nHHHHHH tids", tids
	#print "\n\n\ntidPosGridThisLev\n", tidPosGridThisLev
	levProg = warpUi.getOfsWLev(lev) % 1.0
	dud = fragmod.shadeImgGrid(
			np.int32(warpUi.res[0]),
			np.int32(warpUi.res[1]),
			np.int32(lev),
			np.int32(len(tids)),
			np.float32(levProg),
			np.float32(levPct),
			np.float32(tripFrK),
			np.float32(warpUi.parmDic("clrKBig")),
			np.float32(kRip),
			np.float32(warpUi.parmDic("moveK")),
			np.float32(warpUi.parmDic("moveUseAsBiggest")),
			np.float32(warpUi.parmDic("moveBiggestPow")),
			np.float32(warpUi.parmDic("moveKForBiggest")),
			np.float32(warpUi.parmDic("moveRippleSpeed")),
			np.float32(warpUi.parmDic("moveKofs")),
			np.float32(warpUi.parmDic("centX")),
			np.float32(warpUi.parmDic("centY")),
			np.float32(warpUi.parmDic("satClr")),
			np.float32(warpUi.parmDic("multClr")),
			np.float32(warpUi.parmDic("solidClr")),
			np.int32(warpUi.parmDic("style0x1y2rad")),
			np.int32(warpUi.parmDic("leftToRight")),
			np.int32(warpUi.parmDic("topToBottom")),
			np.int32(warpUi.parmDic("radiateTime")),
			np.int32(warpUi.parmDic("edgeThick")),
			np.int32(bgMode),
			np.int32(frWOfs),
			np.array(inhFrames, dtype=np.intc),
			np.array(exhFrames, dtype=np.intc),
			np.array(brFrames, dtype=np.intc),
			np.array(warpUi.cInOutVals, dtype=np.float32),
			np.array(srcImgAr, dtype=np.intc),
			#np.array(tidImgLs, dtype=np.intc),
			np.array(tidPosGridThisLev, dtype=np.intc),
			np.array(tids, dtype=np.intc),
			np.array(bbxs, dtype=np.intc),
			np.array(xfs, dtype=np.float32),
			np.array(isBulbs, dtype=np.float32),
			np.array(tidTrips, dtype=np.intc),
			aovRipImg,
			alphaBoostImg,
			shadedImg,
			shadedImgXf)

	#print "\n-------------shadedImg[10][10]:", shadedImg[10][10], "\n"
		
	#shadedImgSrf = pygame.surfarray.make_surface(shadedImg)
	#pygame.image.save(shadedImgSrf, "/tmp/shadedImgSrf.%05d.png" % fr)
	#pygame.image.save(shadedImgXfSrf, "/tmp/shadedImgXfSrf.%05d.png" % fr)

	#return pygame.surfarray.make_surface(shadedImg)
	#return [
	#	("ren", pygame.surfarray.make_surface(shadedImg)), 
	#	("rip", pygame.surfarray.make_surface(aovRipImg))]


def getTripFrK(warpUi): 
	tripFrStart = warpUi.parmDic("tripFrStart")
	#tripKMid = .2
	tripKMid = warpUi.parmDic("tripKMid")
	if warpUi.parmDic("tripAlwaysOn") == 1:
		tripFrK = 1
	else:
		fr = warpUi.parmDic("fr")
		# TODO Incorporate trip lev into breath.
		nxFr,nxVal = warpUi.getNextBr(fr,incl=True)
		pvFr,pvVal = warpUi.getPrevBr(fr)

		sm = ut.smoothstep(pvFr, nxFr, fr + 110)  # Hack to get ~x2350 looking right
		sm *= sm*sm # Should make a more exlosive ramp up to breath.
		tripFrK = ut.mix(pvVal, nxVal, sm)
		print "\n\n_getTripFrK(): fr", fr, "pvFr", pvFr, "nxFr", nxFr
		print "_getTripFrK(): tripFrK", tripFrK, "pvVal", pvVal, "nxVal", nxVal

	tripFrK *= tripFrK
	return tripFrK


def generalTripToClrTrip(trip):
	return trip



def render(warpUi): 
	ut.timerStart(warpUi, "render")
	srcImg = pygame.image.load(warpUi.images["source"]["path"])
	res = srcImg.get_size()
	tidPosGridZero = np.zeros((res[0], res[1]), dtype=np.intc)

	print "\n_render(): BEGIN"

	tripFrK = getTripFrK(warpUi)
	print "_render(): tripFrK:", tripFrK

	#tidPosGridThisLevA = warpUi.tidPosGrid[warpUi.levsToRen[0]]
	#shape3d = (len(tidPosGridThisLevA)+1, len(tidPosGridThisLevA[0])+1, 3)
	shape3d = res + (3,)
	shadedImgXf, dud = makeBufferOutput(warpUi, shape3d)

	if True:
		shadeImg(
			warpUi,
			1, # bgMode,
			0, # lev,
			srcImg,
			tidPosGridZero, # tidPosGridThisLev,
			[], # tids, # STASH
			[], # bbxs, # STASH,
			[], # xfs, # STASH though this [sh|c]ould be calculated on the fly
			[], # tidTrips,
			0, # tripFrK,
			[], #isBulbs,
			shadedImgXf)


	fr, frameDir = warpUi.makeFramesDataDir()
	for lev in range(warpUi.parmDic("nLevels")):
		ut.timerStart(warpUi, "preshade")
		ut.timerStart(warpUi, "preshade1")
		if not lev in warpUi.levsToRen:
			continue

		#for stashedBasename in ["isBulbs", "tidTrips", "bbx1d", "tids", "xfs", "tidPosGridThisLev"]:
		#	stashedPath = frameDir + ("/lev%02d." % lev) + stashedBasename
		#	if not os.path.exists(stashedPath):
		#		print "\nUUUUUUUUNNNNNNNNNNNNNNN_render():", stashedPath, "DOES NOT EXIST!  Writing stashed data..."
		#		warpUi.writeStash = True
		#		break
		print "\n\n\nJJJJJJJJJJJJJJJ _render(): warpUi.writeStash:", warpUi.writeStash
		if warpUi.writeStash:
			tidPosGridThisLev = np.array(warpUi.tidPosGrid[lev], dtype=np.intc)
			tidToSidsThisLev = warpUi.tidToSids[lev]

			# Pad to fit img dimensions - no tid for last x or y.
			tidPosGridThisLev = np.lib.pad(tidPosGridThisLev, ((1,0), (0,1)), "constant", constant_values=-1)
			tids = tidToSidsThisLev.keys()
			if tids == []:
				continue
			tids.sort()
			print "_render(): Generating sprites for lev", lev, "len(tids) =", len(tids)

			tidClrGrid = converTidPosGridToTidClrGrid(tidPosGridThisLev, tids)
			tidImg = pygame.surfarray.make_surface(tidClrGrid)




			print "\n PRE-SHADE-111111111 TIME",  ut.timerStop(warpUi, "preshade1")


			bbxs = []
			xfs = []
			tidProgs = []
			tidTrips = []
			isBulbs = []
			res = warpUi.res
			imgCent = (res[0]/2, res[1]/2)
			#centToCnr = math.sqrt(imgCent[0]*imgCent[0] + imgCent[1]*imgCent[1])
			centToCnr = ut.vLen(imgCent)
			#print "\n\n &&&&&&&&&&&&&&&&&&&&&&&&&&&&& LAST TID====", tids[len(tids)-1]
			print "_render(): pre tid loop..."
			bbx1d = [-1] * len(tids) * 4
			#print "EEEEEEEEEE len(bbx1d)", len(bbx1d), "tids", tids, "\n\n"
			for tidPos,tid in enumerate(tids):

				# Get tidProg.
				levProg = warpUi.getOfsWLev(lev) % 1.0
				progDurMin = .6
				progDurMax = 1

				random.seed(tid)
				progDur = ut.mix(progDurMin, progDurMax, random.random())
				progStart = (1.0 - progDur) * random.random()
				tidProg = ut.smoothlaunch(progStart, progStart + progDur, levProg)
				
				fr = warpUi.parmDic("fr")
				dud,breaths,dud = zip(*warpUi.breathsNameFrTrip)
				inhFrames = breaths[0::2]
				breathsAr = np.array(inhFrames, dtype=np.intc)

				tidTrip = tidProg * tripFrK

				tidProgs.append(int(tidProg*100))
				tidTrips.append(int(tidTrip*100))

				isBulb = 0

				if "bbx" in tidToSidsThisLev[tid]:
					bbx = tidToSidsThisLev[tid]["bbx"]
					sz = (bbx[1][0] - bbx[0][0], bbx[1][1] - bbx[0][1])
					cent = ((bbx[1][0]+bbx[0][0])/2, (bbx[1][1]+bbx[0][1])/2)

					dToCent = ut.vDist(imgCent, cent)
					dNorm = float(dToCent)/centToCnr

					#print "_render() tidPos:", tidPos, ";  tid:", tid, ";  bbx:", bbx
					bbxTup = (bbx[0][0], bbx[0][1], bbx[1][0], bbx[1][1])
					bbxs.append(bbxTup)
					bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
					for j in range(4):
						#print "tidPos*4", tidPos*4, "len(bbx1d)", len(bbx1d), "tids", tids, "\n\n"

						bbx1d[tidPos*4 + j] = bbxTup[j] - (1 if j < 2 else 0)

					inRip = fragmod.calcInRip(fr, breathsAr, len(breathsAr), dNorm, 1)
					kRip = 3
					tidTrip = tidProg
					tidTrip = pow(tidTrip, max(0, 1.0/(1+inRip*kRip)))
					#print "----------------inRip", inRip, "dNorm", dNorm, "breathsAr", breathsAr
					#tidTrip *= 1+2*inRip
					tidTrip = tidTrip * tripFrK # Already calculated, but add rip


					tidTrips[-1] = int(tidTrip*100) # TODO: Make float;
					xf = calcXf(warpUi, tidTrip, bbxTup)
					xfs.append(xf)


					# Bulb
					bulbSzMin = .01# .01
					bulbSzMax = .06# .1
					bulbFrPeriod = 20
					bulbDistPeriod = .25
					bulbDistSegments = 3
					bulbFade = .2
					bulbOnPct = .6
					bulbSquareTolerance = .1

					yByXRes = float(res[1])/res[0]

					isBulb = 0
					enableBulb = False
					if enableBulb and sz[0] > 0 and sz[1] > 0:
						szRel = (float(sz[0])/res[0], float(sz[1])/res[1])
						szRatio = szRel[0]/szRel[1]
						#print "\n XXXXXXXXXXXXXXXx bbx", bbx, "sz", sz, "szRel", szRel, "szRatio", szRatio, "cent", cent


						if (szRel[0] > bulbSzMin*yByXRes and
							szRel[0] < bulbSzMax*yByXRes and
							szRel[1] > bulbSzMin and
							szRel[1] < bulbSzMax and
							szRatio < 1 + bulbSquareTolerance and
							szRatio < 1 - bulbSquareTolerance):
								#bordTotal < 1: 
							dSegment = math.floor((1-dNorm)/bulbDistPeriod)
							frBulb = fr + bulbFrPeriod*float(dSegment)/bulbDistSegments

							inPeriod = float(frBulb % bulbFrPeriod)/bulbFrPeriod
							isBulb = ut.smoothpulse(0, bulbFade*bulbOnPct, bulbOnPct-bulbFade*bulbOnPct, bulbOnPct, inPeriod) * tripFrK



				else:
					print "\n\n UUUUUUUUUUUUUUUUUUUUUUUU _render(): Reading stashed data..."
					xfs.append((0.0,0.0)) # To keep tidPos synched.
				isBulbs.append(isBulb)


			#for i in range(0, len(tids), 20):
			#	print "i", i, "bbx1d[i*4:i*4+4]", bbx1d[i*4:i*4+4], "bbxs[i]", bbxs[i]

			
			print "\n\npickleDumping....."
			#pickleDump("/tmp/fr%05d.lev%02d.isBulbs" % (fr, lev), isBulbs)
			#pickleDump("/tmp/fr%05d.lev%02d.tidTrips" % (fr, lev), tidTrips)
			#pickleDump("/tmp/fr%05d.lev%02d.bbx1d" % (fr, lev), bbx1d)
			#pickleDump("/tmp/fr%05d.lev%02d.tids" % (fr, lev), tids)
			#pickleDump("/tmp/fr%05d.lev%02d.xfs" % (fr, lev), xfs)
			#pickleDump("/tmp/fr%05d.lev%02d.tidPosGridThisLev" % (fr, lev), tidPosGridThisLev)
			pickleDump(frameDir + ("/lev%02d.isBulbs" % lev), isBulbs)
			pickleDump(frameDir + ("/lev%02d.tidTrips" % lev), tidTrips)
			pickleDump(frameDir + ("/lev%02d.bbx1d" % lev), bbx1d)
			pickleDump(frameDir + ("/lev%02d.tids" % lev), tids)
			pickleDump(frameDir + ("/lev%02d.xfs" % lev), xfs)
			pickleDump(frameDir + ("/lev%02d.tidPosGridThisLev" % lev), tidPosGridThisLev)

			tidPosGridClr = np.zeros(tidPosGridThisLev.shape + (3,), dtype=np.intc)


			xr = tidPosGridThisLev.shape[0]
			yr = tidPosGridThisLev.shape[1]
			fragmod.arrayIntToClr(
				xr,
				yr,
				tidPosGridThisLev,
				tidPosGridClr)

			tidPosGridClr = tidPosGridClr.astype(np.uint8)

			tidPosGridThisLevImg = Image.fromarray(np.swapaxes(tidPosGridClr, 0, 1), 'RGB')
			#tidPosGridThisLevImg = Image.fromarray(tidPosGridClr, 'RGB')
			tidPosGridThisLevImg.save(frameDir + ("/lev%02d.tidPosGridClr.png" % lev))

			#pygame.image.save(tidImg, "/tmp/fr%05d.lev%02d.tidImg" % (fr, lev))
			print "\n\nDone pickleDumping....."
		else:
			loadTidPosGridClr = True # TEMP
			if loadTidPosGridClr:
				tidPosGridThisLevImg = Image.open(frameDir + "/lev%02d.tidPosGridClr.png" % lev)

				# Reorient the image correctly.
				tidPosGridThisLevImg = tidPosGridThisLevImg.transpose(Image.FLIP_LEFT_RIGHT)
				tidPosGridThisLevImg = tidPosGridThisLevImg.rotate(90, expand=True)
				sz = tidPosGridThisLevImg.size
				tidPosGridThisLevImg = tidPosGridThisLevImg.crop((1, 1, sz[0], sz[1]))
				tidPosGridClr = np.asarray(tidPosGridThisLevImg, dtype=np.intc)
				tidPosGridThisLevLoad = np.zeros(tidPosGridClr.shape[:2], dtype=np.intc)
				tidPosGridClrTEST = np.zeros(tidPosGridClr.shape, dtype=np.intc)
				#if True:
				#	print "\n\nHHHHHHHHH doing loop..."
				#	for xx in range(len(tidPosGridThisLevLoad)):
				#		for yy in range(len(tidPosGridThisLevLoad[0])):
				#			tidPosGridThisLevLoad[xx][yy] = -1 if tidPosGridClr[xx][yy][2] == 200 else tidPosGridClr[xx][yy][0] + tidPosGridClr[xx][yy][1]*256
				#	print "HHHHHHHHH done loop..."
				if True:
					tidPosGridThisLevLoadC = np.zeros(tidPosGridClr.shape[:2], dtype=np.intc)
					#tidPosGridThisLevLoadC = np.swapaxes(tidPosGridThisLevLoadC, 0, 1)
					xr = tidPosGridThisLevLoadC.shape[0]
					yr = tidPosGridThisLevLoadC.shape[1]

					#print "tidPosGridClr[3]", tidPosGridClr[3]
					#print "tidPosGridClr[3][4]", tidPosGridClr[3][4]
					#tidPosGridThisLevLoadC = np.swapaxes(tidPosGridThisLevLoadC, 0, 1)
					tidPosGridThisLevLoadC = tidPosGridThisLevLoadC
					fragmod.arrayClrToInt(
						xr,
						yr,
						tidPosGridClr,
						tidPosGridThisLevLoadC)



			ut.timerStart(warpUi, "pickleLoad")
			print "\n\npickleLoading....."
			isBulbs = pickleLoad(frameDir + ("/lev%02d.isBulbs" % lev))
			tidTrips = pickleLoad(frameDir + ("/lev%02d.tidTrips" % lev))
			bbx1d = pickleLoad(frameDir + ("/lev%02d.bbx1d" % lev))
			tids = pickleLoad(frameDir + ("/lev%02d.tids" % lev))
			xfs = pickleLoad(frameDir + ("/lev%02d.xfs" % lev))
			#tidPosGridThisLev = pickleLoad(frameDir + ("/lev%02d.tidPosGridThisLev" % lev))
			#tidPosGridThisLev = np.swapaxes(tidPosGridThisLevLoadC, 0, 1)
			tidPosGridThisLev = tidPosGridThisLevLoadC

			#for xx in range(0, len(tidPosGridThisLev), 10):
			#	for yy in range(0, len(tidPosGridThisLev[0]), 10):
			#		if not tidPosGridThisLev[xx][yy] == tidPosGridThisLevLoad[xx][yy]:
			#			print "\nxx", xx, "yy", yy, "tidPosGridThisLev[xx][yy]    :",  tidPosGridThisLev[xx][yy]
			#			print "xx", xx, "yy", yy, "tidPosGridThisLevLoad[xx][yy]:", tidPosGridThisLevLoad[xx][yy]
			#		else:
			#			print "ok"


			#isBulbs = pickleLoad("/tmp/fr%05d.lev%02d.isBulbs" % (fr, lev))
			#tidTrips = pickleLoad("/tmp/fr%05d.lev%02d.tidTrips" % (fr, lev))
			#bbx1d = pickleLoad("/tmp/fr%05d.lev%02d.bbx1d" % (fr, lev))
			#tids = pickleLoad("/tmp/fr%05d.lev%02d.tids" % (fr, lev))
			#xfs = pickleLoad("/tmp/fr%05d.lev%02d.xfs" % (fr, lev))
			#tidPosGridThisLev = pickleLoad("/tmp/fr%05d.lev%02d.tidPosGridThisLev" % (fr, lev))
			#pygame.image.save(tidImg, "/tmp/fr%05d.lev%02d.tidImg" % (fr, lev))
			print "\n\nDone pickleLoading....."
			print "\n PICKLE LOAD TIME",  ut.timerStop(warpUi, "pickleLoad")

			ut.timerStart(warpUi, "postpick")
			bbxs = []
			for i in range(0, len(tids)):
				bbxs.append(tuple(bbx1d[i*4 : (i+1)*4]))
				#print "i", i, "bbx1d[i*4:i*4+4]", bbx1d[i*4:i*4+4], "bbxs[i]", bbxs[i]
			print "\n POST-PICKLE TIME",  ut.timerStop(warpUi, "postpick")
		print "\n PRE-SHADE TIME",  ut.timerStop(warpUi, "preshade")

		ut.timerStart(warpUi, "shade")

		bgMode = 0;
		shadeImg(
			warpUi,
			bgMode,
			lev,
			srcImg,
			tidPosGridThisLev,
			tids, # STASH
			bbxs, # STASH,
			xfs, # STASH though this [sh|c]ould be calculated on the fly
			tidTrips,
			tripFrK,
			isBulbs,
			shadedImgXf)
		print "\n SHADE TIME",  ut.timerStop(warpUi, "shade")


	shadedImgXfSrf = pygame.surfarray.make_surface(shadedImgXf)
	renImgPath = warpUi.images["ren"]["path"]
	renSeqDir = "/".join(renImgPath.split("/")[:-1]) #TODO: Do this with os.path.
	ut.mkDirSafe(renSeqDir)
	pygame.image.save(shadedImgXfSrf, renImgPath)
	renderTime = ut.timerStop(warpUi, "render")
	print "\n\n VVVVVVVVVvvv warpUi.writeStash", warpUi.writeStash, "renderTime", renderTime




def getMoveKProg(warpUi, frOfs):
	if warpUi.parmDic("moveDirOverride") == "n":
		inOuts = [warpUi.parmDic("tripFrStart"),
			warpUi.parmDic("inh0"), 
			warpUi.parmDic("exh0"), 
			warpUi.parmDic("inh1"), 
			warpUi.parmDic("exh1"), 
			warpUi.parmDic("inh2"), 
			warpUi.parmDic("exh2"), 
			warpUi.parmDic("inh3"), 
			warpUi.parmDic("exh3"),
			warpUi.parmDic("frEnd"),
			] 


		nx = 0
		pv = 0
		sign = 1
		ii = 0
		for i,v in enumerate(inOuts):
			if v > frOfs:
				pv = 0 if i == 0 else inOuts[i-1]
				nx = v
				if i % 2 == 1:
					ii = i
					sign = -1
				break
		
		#print "\nfrOfs", frOfs, "pv", pv, "nx", nx, "ii", ii
		if pv == 0:
			moveKProg = 0
		else:
			prog = ut.smoothstep(pv, nx, frOfs)
			k = ut.smoothpulse(pv, (pv+nx)/2,  (pv+nx)/2, nx, frOfs)
			moveKProg = sign * k
			#if pv == warpUi.parmDic("tripFrStart"):
			#	moveKProg = -prog
			#else:
			#	moveKProg = sign * ut.mix(-1, 1, prog)
		
		fr = warpUi.parmDic("fr")
		#print "\n_getMoveKProg(): inOuts", inOuts
		#print "_getMoveKProg(): fr", fr, " frOfs", frOfs, "ii", ii, "pv", pv, "nx", nx, "sign", sign, "prog", prog, "moveKProg", moveKProg
		
	else:
		#print "\n\n ***** setting moveKProg to", float(warpUi.parmDic("moveDirOverride"))
		moveKProg = float(warpUi.parmDic("moveDirOverride"))

	return moveKProg


def calcXf(warpUi, tidProg, bbxTup):
	res = warpUi.res

	sz = (bbxTup[2] - bbxTup[0], bbxTup[3] - bbxTup[1]) 

	rels = (float(sz[0])/res[0]) * (float(sz[1])/res[1])
	
	#if sz[0] > 10:
	#	print "res", res, "sz", sz, "rels", rels
	relsPostSmooth = ut.smoothstep(0, warpUi.parmDic("moveUseAsBiggest"), rels)
	relsPostSmooth = pow(relsPostSmooth, warpUi.parmDic("moveBiggestPow"))
	
	moveKBig = ut.mix(1.0, warpUi.parmDic("moveKForBiggest"), relsPostSmooth)

	tCent = ((bbxTup[0] + bbxTup[2])/2, (bbxTup[1] + bbxTup[3])/2) 
	centX = warpUi.parmDic("centX")
	centY = warpUi.parmDic("centY")
	pCent = (centX*res[0], centY*res[1]/2)
	dFromCentXy = (tCent[0]-pCent[0], tCent[1]-pCent[1])

	#dFromCent = math.sqrt(dFromCentXy[0]*dFromCentXy[0] + dFromCentXy[1]*dFromCentXy[1])
	dFromCent = ut.vLen(dFromCentXy)/float(res[0]/2)
	fr = warpUi.parmDic("fr")
	moveRippleOfs = .2
	frOfs = fr - (dFromCent-moveRippleOfs) * warpUi.parmDic("moveRippleSpeed")
	frOfs += 55 # Hack that seems to work?
	k = tidProg*moveKBig*warpUi.parmDic("moveK")*(warpUi.parmDic("moveKofs")) # moveKProg not needed post-cig
	style0x1y2rad = warpUi.parmDic("style0x1y2rad")
	if style0x1y2rad == 0:
		xf = (dFromCentXy[0]*k, 0)
	elif style0x1y2rad == 1:
		xf = (0, dFromCentXy[1]*k)
	else:
		xf = (dFromCentXy[0]*k, dFromCentXy[1]*k)
	return xf




def getFadeout(fr):
	return 1 # - ut.smoothstep(3135, 3230, fr) NO FADE OUT YET


def renWrapper(warpUi):


	renWrapperStartTime = time.time()
	print "\n_renWrapper(): BEGIN"
	fr, frameDir = warpUi.makeFramesDataDir(doMake=False)
	frPerCycle = warpUi.parmDic("frPerCycle")
	backupDataEvery = warpUi.parmDic("backupDataEvery")
	# Load tidToSids when you don't have one, or every frPerCycle frames.
	if warpUi.tidToSids == None:
		print "_renWrapper(): warpUi.tidToSids == None"
	else:
		print "_renWrapper(): warpUi.tidToSids NOT == None"
	if warpUi.tidToSids == None or fr == warpUi.parmDic("frStart") \
			or fr % backupDataEvery == 0:
		# Load tidToSids
		print "_renWrapper(): Updating tidToSids"
		framesDir = warpUi.seqDataVDir + "/frames"
		nextSafeTidFr = fr + frPerCycle # ensure all tids have been merged.
		frToLoad = backupDataEvery*int(math.ceil(
			float(nextSafeTidFr)/backupDataEvery)) # next fr that has backup.
		dicPathToLoad = warpUi.seqDataVDir + ("/frames/%05d/tidToSids" % frToLoad)

		if os.path.exists(dicPathToLoad):
			# Load NEXT suitable tidToSids
			print "_renWrapper(): loading dicPathToLoad..."
			warpUi.tidToSids = pickleLoad(dicPathToLoad)
		else:
			# Load LAST tidToSids
			print "_renWrapper(): dicPathToLoad not found, attempting to load latest..."
			loadLatestTidToSids(warpUi)

	forceGenTidPosGrid = True # TODO: Do you ever want this False?

	warpUi.writeStash = False
	for lev in warpUi.levsToRen:
		for stashedBasename in ["isBulbs", "tidTrips", "bbx1d", "tids", "xfs", "tidPosGridThisLev"]:
			stashedPath = frameDir + ("/lev%02d." % lev) + stashedBasename
			if not os.path.exists(stashedPath):
				print "\nUUUUUUUUNNNNNNNNNNNNNNN_render():", stashedPath, "DOES NOT EXIST!  Writing stashed data..."
				warpUi.writeStash = True
				break
		if warpUi.writeStash == True:
			break
	if warpUi.writeStash == False or forceGenTidPosGrid == False and (not warpUi.tidPosGrid == None) and warpUi.dataLoadedForFr == fr:
		print "_renWrapper(): tidPosGrid already loaded for fr " \
			+ str(fr) + ", reusing."
	else:
		tidPosGridPath = warpUi.framesDataDir + ("/%05d/tidPosGrid" % fr)
		print "_renWrapper(): Checking for existence of", tidPosGridPath, "..."
		sidToCvDicPath = frameDir + "/sidToCvDic"
		if os.path.exists(sidToCvDicPath):  # TODO remove all sidToCvDicPath (cv) stuff?
			warpUi.sidToCvDic = pickleLoad(sidToCvDicPath)
		#tholds = pickleLoad(frameDir + "/tholds")
		if forceGenTidPosGrid == False and os.path.exists(tidPosGridPath):
			print "_renWrapper():", tidPosGridPath, "exists.  Loading..."
			warpUi.tidPosGrid = pickleLoad(tidPosGridPath)
			warpUi.dataLoadedForFr = fr
		else:
			print "_renWrapper():", tidPosGridPath, " DOES NOT exist.  Creating with _inSurfGridToTidGrid()..."
			warpUi.tidPosGrid = inSurfGridToTidGrid(warpUi)
			pickleDump(tidPosGridPath, warpUi.tidPosGrid)
			warpUi.dataLoadedForFr = fr
			print "\n_renWrapper(): post _inSurfGridToTidGrid...\n\n"
	#renTidGridGPU(warpUi)
	render(warpUi)
	print "_renWrapper(): END - time =", time.time() - renWrapperStartTime;



def calcProg(warpUi, sid, level, lev):
	random.seed(sid)
	levRel = float(lev)/(warpUi.parmDic("nLevels")-1)
	progDur = ut.mix(warpUi.parmDic("progDurBot"), warpUi.parmDic("progDurTop"), levRel)
	progStartMin = 0
	progStart = ut.mix(progStartMin, 1-progDur, random.random())
	#progStart = ut.mix(progStartMin, 1-progDur*(1-progStartMin), random.random())
	#progEnd = min(1.0, progStart+warpUi.parmDic("progDur"))
	progEnd = progStart + progDur
	#progEnd = progStart + progDur
	#return ut.smoothstep(progStart, progEnd, level)
	return min(1, ut.smoothstep(progStart, progEnd, level))


def inSurfGridToTidGrid(warpUi):

	fr = warpUi.parmDic("fr")
	nLevels = warpUi.parmDic("nLevels")
	res = warpUi.res

	print "inSurfGridToTidGrid(): Converting tidToSids to sidToTidPos..."
	sidToTidPos = [{} for lev in range(nLevels)]
	for lev in range(nLevels):
		tids = warpUi.tidToSids[lev].keys()
		tids.sort()
		tidPos = 0
		#for tid, vals in warpUi.tidToSids[lev].items():
		for tid in tids:
			vals = warpUi.tidToSids[lev][tid]
			for sid in vals["sids"]:
				#sidToTidPos[lev].append((sid, tid))
				#sidToTidPos[lev][sid] = tid
				sidToTidPos[lev][sid] = tidPos
			tidPos += 1


	inSurfGridPath = warpUi.framesDataDir + ("/%05d/inSurfGrid" % fr)
	inSurfGrid = pickleLoad(inSurfGridPath)

	tidPosGrid = []
	maxTid = -1
	for lev in range(nLevels):
		if not lev in warpUi.levsToRen:
			tidPosGrid.append(None)
			continue


		setTidPosGridC = True
		if setTidPosGridC:
			print "_inSurfGridToTidGrid(): Making tidPosGridThisLev for lev - WITH C", lev
			sidsPosSorted = sidToTidPos[lev].items()
			sidsPosSorted.sort()

			tidPosGridThisLevTest = np.zeros((res[0], res[1]), dtype=np.intc)
			tidPosGridThisLevTest.fill(-1)
			#print "\n\n JJJJJJJJJJJJJ tidPosGridThisLevTest", tidPosGridThisLevTest

			if len(sidsPosSorted) > 0:
				sidsSorted,posSortedBySid = zip(*sidsPosSorted)
				#print "\n\n IIIIIIIII posSortedBySid", posSortedBySid
				#print "\n\n HHHHHH sidsPosSorted:"
				#for ss in sidsPosSorted:
				#	print ss

				

				if inSurfGrid and inSurfGrid[lev]:
					print "inSurfGrid PRE", inSurfGrid[lev][10][10]
					# Replace None with -1 - dunno why
					# inSurfGridNoNone = inSurfGrid[lev][:] creates ref instead of copy
					inSurfGridNoNone = np.zeros((len(inSurfGrid[0]), len(inSurfGrid[0][0])))
					for xx in range(len(inSurfGridNoNone)):
						for yy in range(len(inSurfGridNoNone[0])):
							if inSurfGrid[lev][xx][yy] == None:
								inSurfGridNoNone[xx][yy] = -1
							else:
								inSurfGridNoNone[xx][yy] = inSurfGrid[lev][xx][yy]

					print "inSurfGrid POST", inSurfGrid[lev][10][10]
					#tidPosGridThisLevTest = np.array([[[] for yy in range(res[1])] for xx in range(res[0])],
					fragmod.setTidPosGrid(
						res[0],
						res[1],
						len(sidsSorted),
						np.array(sidsSorted, dtype=np.intc),
						np.array(posSortedBySid, dtype=np.intc),
						np.array(inSurfGridNoNone, dtype=np.intc),
						tidPosGridThisLevTest)
			tidPosGridThisLev = np.asarray(tidPosGridThisLevTest)
					
		else:
			print "_inSurfGridToTidGrid(): Making tidPosGridThisLev for lev - NO C", lev
			tidPosGridThisLev = [[[] for yy in range(res[1])] for xx in range(res[0])]
			sidSet = set(sidToTidPos[lev].keys())
			for xx in range(res[0]):
				for yy in range(res[1]):
					if inSurfGrid == None or inSurfGrid[lev] == None:
						tidPosGridThisLev[xx][yy] = -1
					else:
						# print "\n\n\nUUUUUUUUUU xx", xx, "yy", yy, "lev", lev, "res", res
						# print "UUUUUUUUUU len(inSurfGrid)", len(inSurfGrid)
						# print "UUUUUUUUUU len(inSurfGrid[0])", len(inSurfGrid[0])
						# print "UUUUUUUUUU len(inSurfGrid[0][0])", len(inSurfGrid[0][0])
						sid = inSurfGrid[lev][xx][yy]
						if sid == None:
							tidPosGridThisLev[xx][yy] = -1
						elif sid in sidSet:
							tidPosGridThisLev[xx][yy] = sidToTidPos[lev][sid]
							maxTid = max(maxTid, tidPosGridThisLev[xx][yy])
						else:
							tidPosGridThisLev[xx][yy] = 0
		#print "\n\nVVVVVVVVVV", tidPosGridThisLevTest[xx][yy], tidPosGridThisLev[xx][yy]
		for xx in range(len(tidPosGridThisLevTest)):
			#print
			for yy in range(len(tidPosGridThisLevTest[0])):
				# if not tidPosGridThisLevTest[xx][yy] == tidPosGridThisLev[xx][yy]:
				# 	if not 0 == tidPosGridThisLevTest[xx][yy]:
				# 		print ("%d:%d" % (tidPosGridThisLevTest[xx][yy], tidPosGridThisLev[xx][yy])),
				if 0 == tidPosGridThisLev[xx][yy]:
					print ("%d:%d" % (tidPosGridThisLevTest[xx][yy], tidPosGridThisLev[xx][yy])),
		tidPosGrid.append(tidPosGridThisLev)
	
	return tidPosGrid




