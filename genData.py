#!/usr/bin/python
import pygame, math, ut, os, pprint, sys, random, time, shutil, glob
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
	texClr = None
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
	kSurf = warpUi.parmDic("kSurf")
	res = img.get_size()
	nJoints = 0
	tholds = [None for lev in range(nLevels)]
	
	ut.timerStart(warpUi, "initJtGridXYLoop")

	jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
	tryGPU = True
	if tryGPU:
		# Mark dirty before GPU ops in case of crash.
		ut.indicateProjDirtyAs(warpUi, True, "initJtGridGPU_inProgress")

		levThreshRemap = []
		levThreshInt = []
		for lev in range(nLevels):
			thisLevThreshRemap, thisLevThreshInt = \
				getLevThresh(warpUi, lev, nLevels)
			levThreshRemap.append(thisLevThreshRemap)
			tholds[lev] = thisLevThreshRemap
			# TODO -> tholds[lev] = thisLevThreshRemap
			levThreshInt.append(thisLevThreshInt)

		print "_initJtGrid(): levThreshInt:", levThreshInt
		print "_initJtGrid(): levThreshRemap:", levThreshRemap
		levThreshArray = np.array(levThreshInt, dtype=np.uint8)
		levThreshArray_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.READ_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=levThreshArray)
		
		try:
			# This appears to break on black frames, dunno cleaner way around it.
			imgArray = np.array(list(pygame.surfarray.array3d(img)))
		except:
			print "OOPS: pygame.surfarray.array3d(img) caused error, setting imgArray to 0.\n\n"
			imgArray = np.zeros(res + (3,), dtype=np.uint8)
		imgArray_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.READ_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=imgArray)
		
		jtCons = np.empty((nLevels, res[0], res[1]), dtype=np.intc)
		jtCons.fill(0)

		jtConsThisLev = np.empty((res[0], res[1]), dtype=np.intc)
		jtConsThisLev.fill(0)
		jtConsThisLev_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY, jtConsThisLev.nbytes)
		
		
		kernelPath = ut.projDir + "/GPUKernel.c"
		with open(kernelPath) as f:
			kernel = "".join(f.readlines()) % (res[1], res[0])
		#int index = rowid * ncols * npix + colid * npix;
		# build the Kernel
		for lev in range(nLevels):
			bld = cl.Program(warpUi.cntxt, kernel).build()
			launch = bld.initJtC(
					warpUi.queue,
					imgArray.shape,
					None,
					np.int32(warpUi.parmDic("nLevels")),
					np.int32(lev),
					imgArray_buf,
					levThreshArray_buf,
					jtConsThisLev_buf)
			launch.wait()


			cl.enqueue_read_buffer(warpUi.queue, jtConsThisLev_buf, jtConsThisLev).wait()
			jtCons[lev] = jtConsThisLev

		# This sez I should release - help mem leak?
		# https://stackoverflow.com/questions/44197206/how-to-release-gpu-memory-use-same-buffer-for-different-array-in-pyopencl
		levThreshArray_buf.release()
		imgArray_buf.release()


	
		for lev in range(nLevels):
			levThreshRemap, levThreshInt = getLevThresh(warpUi, lev, nLevels)
			for x in range(res[0]-1):
				for y in range(res[1]-1):
					jtConsKey = jtCons[lev][x][y]
					#jtConsKey = jtConsThisLev[x][y]
					#print "HHHHHH jtConsKey", jtConsKey
					gpuCons = decodeCons[jtConsKey]
					if len(gpuCons) > 0:
						jtLs = []
						for gpuCon in gpuCons:
							jtLs.append(joint((x,y), levThreshRemap, gpuCon))
						jtGrid[x][y][lev] = jtLs

		# Mark clean after GPU ops.
		ut.indicateProjDirtyAs(warpUi, False, "initJtGridGPU_inProgress")

	else:
		for x in range(res[0]-1):
			if (x+1) % (res[0]/10) == 0:
				print "_initJtGrid(): %d%%" % (((x+1) * 100)/res[0])
			for y in range(res[1]-1):
				# TODO: I 'spect you should do lev loop first, then x,y so you can do all per-lev calcs once.
				# get neighbours.
				nbrs = []
				for yy in range(y, y+2):
					for xx in range(x, x+2):
						nbrs.append(int(avgLs(img.get_at((xx,yy))[:-1])))

				for lev in range(nLevels):
					levThreshRemap, levThreshInt = getLevThresh(warpUi, lev, nLevels)
					tholds[lev] = levThreshRemap

					isHigher = []
					tot = 0
					for nbr in nbrs:
						higher = 1 if nbr > levThreshInt else 0
						tot += higher
						isHigher.append(higher)
					# Only add joint if different.
					if tot > 0 and tot < 4:
						cons = neighboursToConns[tuple(isHigher)]
						texClr = img.get_at((x,y))
						if len(cons) > 1:
							# TODO: I think all these levThresh's, should be levThreshRemap's
							jtGrid[x][y][lev] =  [joint((x,y), levThreshRemap, cons[0]),
												   joint((x,y), levThreshRemap, cons[1])]
							nJoints += 2
						else:
							jtGrid[x][y][lev] = [joint((x,y), levThreshRemap, cons[0])]
							nJoints += 1
	# Write stats

	renPath = warpUi.images["ren"]["path"]
	renSeqDir = "/".join(renPath.split("/")[:-1]) #TODO: Do this with os.path.
	ut.mkDirSafe(renSeqDir)

	ut.timerStop(warpUi, "initJtGridXYLoop")

	return jtGrid, tholds

def setAOV(warpUi, name, dbImgDic, lev, nLevels, x, y, val):
	prevVal = ut.black
	aovParmName = "aov_" + name	
	if aovParmName in warpUi.parmDic.parmDic.keys() and warpUi.parmDic(aovParmName) == 1 and lev <= len(dbImgDic[name]): # TODO: Won't last cond always be true?
		res = dbImgDic[name][lev].get_size()
		if x < res[0] and y < res[1]:
			#prevVal = dbImgDic[name][lev].get_at((x,y))
			newVal = tuple(list(val))
			newVal = ut.clampVSc(newVal, 0, 255)
			dbImgDic[name][lev].set_at((x,y), newVal)
			dbImgDic[name][nLevels].set_at((x,y), newVal)


def drawBbx(warpUi, bbx, dbName, dbImgDic, lev, nLevels, clr):
	# Draw cvBbx
	xmn, ymn = bbx[0]
	xmx, ymx = bbx[1]
	# Vertical lines
	for xx in range(xmn, xmx):
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xx, ymn, clr)
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xx, ymx, clr)
	# Horizontal lines
	for yy in range(ymn, ymx):
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xmn, yy, clr)
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xmx, yy, clr)
	
# From neighboursToConns:
decodeCons = ((),
	(((0, 1), (1, 0)),),
	(((-1, 0), (0, 1)),),
	(((-1, 0), (1, 0)),),
	(((1, 0), (0, -1)),),
	(((0, 1), (0, -1)),),
	(((-1, 0), (0, 1)), ((1, 0), (0, -1)),),
	(((-1, 0), (0, -1)),),
	(((0, -1), (-1, 0)),),
	(((0, 1), (1, 0)), ((0, -1), (-1, 0)),),
	(((0, -1), (0, 1)),),
	(((0, -1), (1, 0)),),
	(((1, 0), (-1, 0)),),
	(((0, 1), (-1, 0)),),
	(((1, 0), (0, 1)),),
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

	# AOVs.
	#dbImgs = ["inSurfNow", "surfsAndHoles", "inPrev", "cid", "cvSid", "cidPost", "sid", "sidPost"]
	dbImgs = []
	for parmName in warpUi.parmDic.parmDic.keys():
		if parmName[:4] == "aov_" and warpUi.parmDic(parmName) == 1:
			dbImgs.append(parmName[4:])

	dbImgDic = {}
	for dbi in dbImgs:
		# The last cell - that is, [nLevels] - is reserved for "all"
		dbImgDic[dbi] = [pygame.Surface(res) for i in range(nLevels+1)][:]



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
			for lev,jts in jtGrid[x][y].items():
				for jt in jts:
					# GPUtrans: I think this can become "if cvGrid[x][y][lev] == None"
					if jt.cv == None:
						# GPUtrans: cvGrid[x][y][lev] = curve(...)
						jt.cv = curve(jt, nCurves, inSurfNow[lev])
						nCurves += 1
						xx = x + jt.cons[1][0]
						yy = y + jt.cons[1][1]
						for jtt in jtGrid[xx][yy][lev]:
							# GPUtrans: [1][0] may become [2], etc.
							if jtt.cons[0][0] == -jt.cons[1][0] and jtt.cons[0][1] == -jt.cons[1][1]:
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
							setAOV(warpUi, "cid", dbImgDic, lev, nLevels, xx, yy, cvClr)
							thisJt.cv = jt.cv
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
	curveId = 0
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
				setAOV(warpUi, "cvSid", dbImgDic, lev, nLevels, xx, yy, sfClr)
				sfClr = ut.intToClr(jt.cv.cid)
				setAOV(warpUi, "cidPost", dbImgDic, lev, nLevels, xx, yy, sfClr)
				jt = jt.pv
				if jt == None:
					break

			# Draw cvBbx
			drawBbx(warpUi, cv.bbx, "cidPost", dbImgDic, lev, nLevels, sfClr)
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
	
	#for lev in range(warpUi.parmDic("nLevels")):
	#	dr, imgPath = warpUi.getDebugDirAndImg("preMrgInSurfGrid", "lev%02d" % lev)
	#	ut.mkDirSafe(dr)
	#	ut.intGridToImg(inSurfGrid[lev], imgPath)


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
					#setAOV(warpUi, "sidPost", dbImgDic, lev, nLevels, x, y, ut.intToClr(sidNew))
	
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
		sidPostImgs[lev].save("/tmp/img." + str(lev) + ".png")
	sidPostImgs.append(Image.fromarray(np.swapaxes(sidPostALL, 0, 1), 'RGB'))

	# Mark clean after GPU ops.
	ut.indicateProjDirtyAs(warpUi, False, "saveSidPostGPU_inProgress")

	for lev in range(nLevels + 1):
		levStr = "ALL" if lev == nLevels else "lev%02d" % lev
		levDir,imgPath = warpUi.getDebugDirAndImg("sidPost", levStr)
		ut.mkDirSafe(levDir)
		print "_growCurves(): saving", imgPath
		sidPostImgs[lev].save(imgPath)


		#for sid in sidToCvs[lev].keys():
		#	drawBbx(warpUi, sidToCvs[lev][sid]["bbx"], "sid", dbImgDic, lev, nLevels, ut.intToClr(sid))
		#for tid, turfData in warpUi.tidToSids[lev].items():
		#	if "bbx" in turfData.keys(): # TODO should bbx always be in turfData.keys()?
		#		drawBbx(warpUi, turfData["bbx"], "sid", dbImgDic, lev, nLevels, ut.intToClr(tid))
		#				#sidToCvs[lev][sidToMergeTo]["cvs"] += sidToCvs[lev][sid]["cvs"]


	# Save db image with new sids.
	print "_growCurves(): Saving debug images", dbImgDic.keys()
	for debugInfo,imgs in dbImgDic.items():
		if not debugInfo == "sidPost":
			for lev in range(nLevels+1):
				levStr = "ALL" if lev == nLevels else "lev%02d" % lev
				levDir,imgPath = warpUi.getDebugDirAndImg(debugInfo, levStr)
				ut.mkDirSafe(levDir)
				pygame.image.save(imgs[lev], imgPath)

	#inSurfGridStr = "POS inSurfGrid:\n"	
	#for y in range(res[1]):
	#	for x in range(res[0]):
	#		inSurfGridStr += str(inSurfGrid[1][x][y]) + " "
	#	inSurfGridStr += "\n"
	#inSurfGridStr += "\n\n"
	#frDirDebug.write(inSurfGridStr)
	#frDirDebug.write("POS warpUi.nextSid:" + str(warpUi.nextSid) + "\n\n")
	#tidToSidsStr = "POS warpUi.tidToSids:\n"
	#ks = warpUi.tidToSids[1].keys()
	#ks.sort()
	#for k in ks:
	#	kks = warpUi.tidToSids[1][k].keys()
	#	kks.sort()
	#	for kk in kks:
	#		tidToSidsStr += str(k) + ":" + str(kk) + ":" + str(warpUi.tidToSids[1][k][kk]) + "\n"
	#	tidToSidsStr += "\n"

	#frDirDebug.write(tidToSidsStr)
	#frDirDebug.close()

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

	# TEMP - aovs to compare prev + cur inSurfGrids.
	#for lev in range(warpUi.parmDic("nLevels")):
	#	if not warpUi.inSurfGridPrev == None:
	#		dr, imgPath = warpUi.getDebugDirAndImg("inSurfGridPrev", "lev%02d" % lev)
	#		ut.mkDirSafe(dr)
	#		ut.intGridToImg(warpUi.inSurfGridPrev[lev], imgPath)

	#	dr, imgPath = warpUi.getDebugDirAndImg("inSurfGrid", "lev%02d" % lev)
	#	ut.mkDirSafe(dr)
	#	ut.intGridToImg(inSurfGrid[lev], imgPath)


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

	# Initialize GPU stuff.
	# ut.indicateProjDirtyAs(warpUi, True, "createContextAndQueue_inProgress")
	# print "_genData(): before _create_some_context()"
	# warpUi.cntxt = cl.create_some_context()
	# print "_genData(): after _create_some_context(); before _CommandQueue"
	# warpUi.queue = cl.CommandQueue(warpUi.cntxt)
	# print "_genData(): after _CommandQueue"
	# ut.indicateProjDirtyAs(warpUi, False, "createContextAndQueue_inProgress")

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




def makeSpriteDic(warpUi, lev, srcImg, tidImg, tids, tidPos, tidToSidsThisLev, tidProgs, tidTrips, xfs):
	tid = tids[tidPos]
	if "bbx" in tidToSidsThisLev[tid]:
		tidProg = tidProgs[tidPos]
		tidTrip = tidTrips[tidPos]
		xf = xfs[tidPos]
		bbx = tidToSidsThisLev[tid]["bbx"]
		if warpUi.parmDic("iso_cs") == "c":
			# Only render curves, no sprite
			spriteImg = None
		else:
		#regen = True
		#if regen:
			sz=(bbx[1][0]-bbx[0][0], bbx[1][1]-bbx[0][1])

			# +1 totally trial + error. ***********???????? maybe not needed?
			bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
			#print "bbxTup", bbxTup

			# Blit bbx of tid from srcImg to empty cropFromSrcImg of bbx size.
			cropFromSrcImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
			cropFromSrcImg.blit(srcImg, (0, 0), bbxTup)
			
			# Fill a sprite-sized np array with tidPosClr based on tidPos.
			tidPosClr = convertTidToClr(tidPos)
			tidClrAr = vecTo3dArray(tidPosClr, sz[0], sz[1])

			#tidClrBbxImg = pygame.surfarray.make_surface(tidClrAr)
			#pygame.image.save(tidClrBbxImg, "test/img/%05d_idClr.png" % tid)

			# Initialize spriteImg with A=0.
			spriteImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
			pygame.surfarray.pixels_alpha(spriteImg)[:,:] = 0

			# Comp tid using tidPosClr colorkey - makes hole at tid.
			tidImg.set_colorkey(tidPosClr)
			spriteImg.blit(tidImg, (0, 0), bbxTup)

			# Invert alpha - TODO: a) quicker (GPU) inversion, ie. OPTIMIZE?
			# b) array_alpha instead because it copies, not references?
			pygame.surfarray.pixels_alpha(spriteImg)[:,:] = \
				invert255V(pygame.surfarray.pixels_alpha(spriteImg)[:,:])
			
			# Copy colours from src.
			pygame.surfarray.pixels3d(spriteImg)[:,:] = \
				pygame.surfarray.pixels3d(cropFromSrcImg)[:,:]


		return {"spriteImg":spriteImg, "bbx":bbx, "tid":tid,
			"tidProg":tidProg, "tidTrip":tidTrip, "xf":xf}
	else:
		return None

def makeBuffer(warpUi, inputList, dtype=None):
	if dtype == None:
		ar = np.array(inputList)
	else:
		ar = np.array(inputList, dtype=dtype)
	return cl.Buffer(warpUi.cntxt, cl.mem_flags.READ_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=ar)
	
	
def renClrTest(warpUi):
	print "\n_renClrTest(): BEGIN\n"
	srcImg = pygame.image.load(warpUi.images["source"]["path"])
	srcImg.fill((255, 0, 255), None, pygame.BLEND_MULT)
	# TODO integrate CLR into AOV system
	destDir = warpUi.seqDataVDir + "/debugImg/CLR"
	ut.mkDirSafe(destDir)
	destPath = destDir + ("/CLR.%05d.png" % warpUi.parmDic("fr"))
	print "\n_renClrTest(): saving srcImg to\n", destPath
	pygame.image.save(srcImg, destPath)
	print "\n_renClrTest(): END\n"

def shadeBg(warpUi, srcImg):
	kernel = """

float mixI(uchar a, uchar b, float m) {
	return m*b + (1.0-m)*a;
}

void mix3(uchar* a, uchar* b, float m, uchar* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixI(a[i], b[i], m);
	}
}

float dist(float x0, float y0, float x1, float y1) {
	float dx = x1-x0;
	float dy = y1-y0;
	return sqrt(dx*dx + dy*dy);
}

void setArrayCell(int x, int y, int xres, int yres,
  uchar* val,
  __global uchar* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}
}

__kernel void krShadeBg(
			int xres,
			int yres,
			__global uchar* shadedImg)
{
	unsigned int x = get_global_id(0);
	unsigned int y = get_global_id(1);
	uchar outClr[3];
	outClr[0] = 255;
	outClr[1] = 10;
	outClr[2] = 200;

	int cx = xres/2;	
	int cy = yres/2;	
	float dFromCent = dist(x, y, cx, cy);
	float dNorm = min(1.0, dFromCent/cx);

	uchar red[] = {20, 0, 0};
	uchar black[] = {0, 0, 0};
	mix3(red, black, dNorm, outClr);
	setArrayCell(x, y, xres, yres+1, outClr, shadedImg);

}

"""
	srcImgLs = list(pygame.surfarray.array3d(srcImg))
	srcImgAr_buf = makeBuffer(warpUi, srcImgLs)
	# Outputs
	shadedImg = np.zeros((len(srcImgLs), len(srcImgLs[0]), len(srcImgLs[0][0])), dtype=np.uint8)
	shadedImg_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=shadedImg)


	bld = cl.Program(warpUi.cntxt, kernel).build()
	launch = bld.krShadeBg(
			warpUi.queue,
			#srcImgAr.shape,
			warpUi.res,
			None,
			np.int32(warpUi.res[0]),
			np.int32(warpUi.res[1]),
			shadedImg_buf)
	launch.wait()
	
	cl.enqueue_read_buffer(warpUi.queue, shadedImg_buf, shadedImg).wait()
		
	return pygame.surfarray.make_surface(shadedImg)

def shadeImg(warpUi, lev, srcImg, tidImg, tidPosGridThisLev,
		tids, bbxs, cents, xfs, tidTrips, tripFrK):
	tidImgLs = list(pygame.surfarray.array3d(tidImg))

	# Inputs
		
	srcImgAr_buf = makeBuffer(warpUi, list(pygame.surfarray.array3d(srcImg)), dtype=np.intc)
	tidImgAr_buf = makeBuffer(warpUi, tidImgLs, dtype=np.intc)
	tidPosGridThisLev_buf = makeBuffer(warpUi, tidPosGridThisLev, dtype=np.intc)
	bbxs_buf = makeBuffer(warpUi, bbxs, dtype=np.intc)
	tids_buf = makeBuffer(warpUi, tids, dtype=np.intc)
	tidTrips_buf = makeBuffer(warpUi, tidTrips, dtype=np.intc)
	xfs_buf = makeBuffer(warpUi, xfs, dtype=np.float32)
	cIn_buf = makeBuffer(warpUi, vX255(warpUi.parmDic("cIn")), dtype=np.intc)
	cOut_buf = makeBuffer(warpUi, vX255(warpUi.parmDic("cOut")), dtype=np.intc)

	# Outputs
	shadedImg = np.zeros((len(tidImgLs), len(tidImgLs[0]), len(tidImgLs[0][0])), dtype=np.intc)
	shadedImg_buf = cl.Buffer(warpUi.cntxt, cl.mem_flags.WRITE_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=shadedImg)

	kernelPath = ut.projDir + "/GPUshadeImg.c"
	with open(kernelPath) as f:
		kernel = "".join(f.readlines())
	
	if warpUi.parmDic("useFilt") > 0:
		kernel = kernel.replace("//USEFILT", "")
		kernel = kernel.replace("/*NOUSEFILT*/", "//")

	
	ofs = warpUi.getOfsWLev(lev) % 1.0
	levPct = int(100*(lev+ofs)/warpUi.parmDic("nLevels")) #int((warpUi.getOfsWLev(lev)*100.0)%100)
	tripGlobPct = int(tripFrK*100)

	bld = cl.Program(warpUi.cntxt, kernel).build()
	print "_shadeImg(): lev", lev, "levPct", levPct
	launch = bld.krShadeImg(
			warpUi.queue,
			#srcImgAr.shape,
			warpUi.res,
			None,
			np.int32(warpUi.res[0]),
			np.int32(warpUi.res[1]),
			np.int32(levPct),
			np.int32(tripGlobPct),
			#np.int32(warpUi.parmDic("useFilt")),
			np.float32(warpUi.parmDic("clrKBig")),
			cIn_buf,
			cOut_buf,
			srcImgAr_buf,
			tidImgAr_buf,
			tidPosGridThisLev_buf,
			tids_buf,
			bbxs_buf,
			xfs_buf,
			tidTrips_buf,
			#cents_buf,
			shadedImg_buf)
	launch.wait()
	

	cl.enqueue_read_buffer(warpUi.queue, shadedImg_buf, shadedImg).wait()
	#print "\n-------------shadedImg[10][10]:", shadedImg[10][10], "\n"
		
	return pygame.surfarray.make_surface(shadedImg)

def genSprites(warpUi, srcImg): 
	spritesThisFr = []

	# Adjust by global seq prog.
	#tripFrStart = 1605
	#tripFrMid = 1640
	#tripFrEnd = 1850
	tripFrStart = warpUi.parmDic("tripFrStart")
	tripFrMid = warpUi.parmDic("tripFrMid")
	tripFrEnd = warpUi.parmDic("tripFrEnd")
	tripKMid = .2
	if warpUi.parmDic("tripAlwaysOn") == 1:
		tripFrK = 1
	else:
		fr = warpUi.parmDic("fr")
		if fr < tripFrMid:
			print "_genSprites(): fr:", fr, "sm:", ut.smoothstep(tripFrStart, tripFrMid, fr)
			tripFrK = tripKMid * ut.smoothstep(tripFrStart, tripFrMid, fr)
		else:
			tripFrK = ut.mix(tripKMid, 1.0, ut.smoothstep(tripFrMid, tripFrEnd, fr))
	print "_genSprites(): tripFrK:", tripFrK
	#tripFrK = 1 # TEMP

	for lev in range(warpUi.parmDic("nLevels")):
		if  warpUi.parmDic("isoLev") > -1 and not lev == warpUi.parmDic("isoLev"):
			spritesThisFr.append({})
			continue

		tidPosGridThisLev = np.array(warpUi.tidPosGrid[lev])
		tidToSidsThisLev = warpUi.tidToSids[lev]

		# Pad to fit img dimensions - no tid for last x or y.
		tidPosGridThisLev = np.lib.pad(tidPosGridThisLev, ((1,0), (0,1)), "constant", constant_values=-1)
		tids = tidToSidsThisLev.keys()
		if tids == []:
			spritesThisFr.append({})
			continue
		tids.sort()
		print "_genSprites(): Doing lev", lev, "len(tids) =", len(tids)

		tidClrGrid = converTidPosGridToTidClrGrid(tidPosGridThisLev, tids)
		tidImg = pygame.surfarray.make_surface(tidClrGrid)
		#path = "test/img/tidImg.lev%03d.%05d.png" % (lev, fr)
		#pygame.image.save(tidImg, path)


		bbxs = []
		cents = []
		xfs = []
		tidProgs = []
		tidTrips = []
		for tidPos,tid in enumerate(tids):

			# Get tidProg.
			levProg = warpUi.getOfsWLev(lev) % 1.0
			progDurMin = .6
			progDurMax = 1

			random.seed(tid)
			progDur = ut.mix(progDurMin, progDurMax, random.random())
			progStart = (1.0 - progDur) * random.random()
			tidProg = ut.smoothstep(progStart, progStart + progDur, levProg)
			
			tidTrip = tidProg * tripFrK

			tidProgs.append(int(tidProg*100))
			tidTrips.append(int(tidTrip*100))

			if "bbx" in tidToSidsThisLev[tid]:
				bbx = tidToSidsThisLev[tid]["bbx"]
				#print "_genSprites() tidPos:", tidPos, ";  tid:", tid, ";  bbx:", bbx
				#bbxs.append(bbx)
				bbxTup = (bbx[0][0], bbx[0][1], bbx[1][0], bbx[1][1])
				bbxs.append(bbxTup)
				#bbxs.append(tidPos)
				#bbxs.append(bbx[0][0])
				#bbxs.append(bbx[0][1])
				cent = ((bbx[0][0] + bbx[0][1])/2, (bbx[1][0] + bbx[1][1])/2) 

				bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
				xf = calcXf(warpUi, tidTrip, bbxTup)
				#xf = calcXf(warpUi, levProg, bbxTup) # TEMP!!!

				cents.append(cent)
				xfs.append(xf)
			else:
				xfs.append((0.0,0.0)) # To keep tidPos synched.

		if warpUi.parmDic("iso_cs") == "c":
			shadedImg = None
		else:
			shadedImg = shadeImg(warpUi, lev, srcImg, tidImg,
				tidPosGridThisLev, tids, bbxs, cents, xfs, tidTrips, tripFrK)

		spritesThisLev = []
		for tidPos in range(len(tids)):
			spriteDic = makeSpriteDic(warpUi, lev, shadedImg, tidImg, tids, tidPos, tidToSidsThisLev, tidProgs, tidTrips, xfs)
			if spriteDic:
				spritesThisLev.append(spriteDic)


		spritesThisFr.append(spritesThisLev)
	return spritesThisFr


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
	pCent = (res[0]/2, res[1]/2)
	dFromCentXy = (tCent[0]-pCent[0], tCent[1]-pCent[1])
	#dFromCent = math.sqrt(dFromCentXy[0]*dFromCentXy[0] + dFromCentXy[1]*dFromCentXy[1])
	dFromCent = ut.vLen(dFromCentXy)/float(res[0]/2)
	fr = warpUi.parmDic("fr")
	moveRippleOfs = .2
	frOfs = fr - (dFromCent-moveRippleOfs) * warpUi.parmDic("moveRippleSpeed")
	moveKProg = getMoveKProg(warpUi, frOfs)

	k = warpUi.parmDic("moveK")*tidProg*moveKBig*(warpUi.parmDic("moveKofs")+moveKProg)
	return (dFromCentXy[0]*k, dFromCentXy[1]*k)


def renCv(warpUi, srcImg, lev, tid, xf, canvas, canvasLev):
	#xfInt = (int(xf[0]), int(xf[1]))
	vals = warpUi.tidToSids[lev][tid]
	for sid in vals["sids"]:
		if sid in warpUi.sidToCvDic[lev].keys():
			cvs = warpUi.sidToCvDic[lev][sid]["cvs"]
			for cv in cvs:
				for jt in cv:
					srcClr = srcImg.get_at(jt)[:-1]
					canvas.set_at((jt[0] + int(xf[0]), jt[1] + int(xf[1])), srcClr)
					#canvas.set_at((jt[0] + xfInt[0], jt[1] + xfInt[1]), (255, 0, 0))
	return None

def renSprites(warpUi, srcImg, res, fr):
	print "\n_renSprites(): BEGIN, fr", fr
	# Initialize canvas
	canvas = pygame.Surface(res, pygame.SRCALPHA, 32)
	canvas.fill((0, 0, 0))
	srcImg = pygame.image.load(warpUi.images["source"]["path"])
	canvas = shadeBg(warpUi, srcImg)
	#for spritesThisLev in spritesThisFr:
	nLevels = warpUi.parmDic("nLevels")

	if warpUi.parmDic("isoLev") > -1:
		levsToRen = [warpUi.parmDic("isoLev")]
		print "\n_renSprites(): ISOLATING LEVEL", levsToRen[0]
	else:
		levsToRen = range(nLevels)
	for lev in levsToRen:
		if False and warpUi.parmDic("iso_cs") == "c":
			for tid in warpUi.tidToSids[lev].keys():
				renCv(warpUi, srcImg, lev, tid, xf, canvas, canvasLev)
		else:
			spritesThisLev = warpUi.spritesThisFr[lev]
			print "_renSprites(): fr", fr, "lev", lev, "len(spritesThisLev)", len(spritesThisLev)
			canvasLev = pygame.Surface(res, pygame.SRCALPHA, 32)
			canvasLev.fill((0, 0, 0))
			for spriteDic in spritesThisLev:
				xf = spriteDic["xf"]
				tid = spriteDic["tid"]
				if not warpUi.parmDic("iso_cs") == "c":
					bbx = spriteDic["bbx"]
					spriteImg = spriteDic["spriteImg"].copy()
					tidProg = .01*spriteDic["tidProg"] # tidProg is int in range (0,100)
					tidTrip = .01*spriteDic["tidTrip"] # tidTrip is int in range (0,100)


					sfFdIn = .2
					sfFdOut = .3
					sfA = warpUi.parmDic("sfA")
					sfK = warpUi.parmDic("sfK")

					levProg = warpUi.getOfsWLev(lev) % 1.0
					surfAlpha = ut.smoothstep(0, sfFdIn, levProg)
					surfAlpha *= 1.0-ut.smoothstep(1-sfFdOut, 1, tidProg)
					#surfAlpha = 1
					#surfAlpha *= sfA # *  ut.smoothpulse(0, sfFdIn, 1-sfFdOut, 1, .01*tidProg)
					pygame.surfarray.pixels_alpha(spriteImg)[:,:] = \
						mult255V(pygame.surfarray.pixels_alpha(spriteImg)[:,:], surfAlpha)

					#spriteImg.fill((225, 0, 0))
					#for dr in dir(pygame.surfarray):
					#	print "\t", dr
					#res = warpUi.res
					#red = np.empty((res[0], res[1]))#, dtype=np.intc)
					#red.fill(0)
					#pygame.surfarray.pixels3d(spriteImg)[0][:,:] = (255, 0, 0)
					bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
					canvas.blit(spriteImg, (bbxTup[0]+xf[0], bbxTup[1]+xf[1]))
					canvasLev.blit(spriteImg, (bbxTup[0]+xf[0], bbxTup[1]+xf[1]))
				if not warpUi.parmDic("iso_cs") == "s":
					renCv(warpUi, srcImg, lev, tid, xf, canvas, canvasLev)

		levStr = "ALL" if lev == nLevels else "lev%02d" % lev
		levDir,imgPath = warpUi.getRenDirAndImgPath("ren", levStr)
		ut.mkDirSafe(levDir)
		pygame.image.save(canvasLev, imgPath)

	renPath = warpUi.images["ren"]["path"]
	renSeqDir = "/".join(renPath.split("/")[:-1]) #TODO: Do this with os.path.
	ut.mkDirSafe(renSeqDir)
	pygame.image.save(canvas, renPath)



def genAndRenSprites(fr, warpUi):	# TODO: Is fr really needed?
	srcImg = pygame.image.load(warpUi.images["source"]["path"])
	res = srcImg.get_size()

	# Only gen sprites if they don't exist or fr is different.
	forceRegen = True
	if forceRegen or warpUi.spritesThisFr == None or (not warpUi.spritesLoadedFr == fr):
		print "_genAndRenSprites(): spritesThisFr don't exist or wrong fr; generating..."
		warpUi.spritesThisFr = genSprites(warpUi, srcImg)
		warpUi.spritesLoadedFr = fr
	else:
		print "_genAndRenSprites(): spritesThisFr exist for this frame, reusing."
	#moveKProg = getMoveKProg(warpUi)
	#renSprites(warpUi, res, fr, moveKProg)
	renSprites(warpUi, srcImg, res, fr)



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
	if forceGenTidPosGrid == False and (not warpUi.tidPosGrid == None) and warpUi.dataLoadedForFr == fr:
		print "_renWrapper(): tidPosGrid already loaded for fr " \
			+ str(fr) + ", reusing."
	else:
		tidPosGridPath = warpUi.framesDataDir + ("/%05d/tidPosGrid" % fr)
		print "_renWrapper(): Checking for existence of", tidPosGridPath, "..."
		sidToCvDicPath = frameDir + "/sidToCvDic"
		if not warpUi.parmDic("iso_cs") == "s" and os.path.exists(sidToCvDicPath):
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
	genAndRenSprites(fr, warpUi)
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
		if  warpUi.parmDic("isoLev") > -1 and not lev == warpUi.parmDic("isoLev"):
			tidPosGrid.append(None)
			continue

		print "_inSurfGridToTidGrid(): Making tidPosGridThisLev for lev", lev
		tidPosGridThisLev = [[[] for yy in range(res[1])] for xx in range(res[0])]
		sidSet = set(sidToTidPos[lev].keys())
		for xx in range(res[0]):
			for yy in range(res[1]):
				#print "lev", lev, "xx", xx, "yy", yy
				#print "len(inSurfGrid)", len(inSurfGrid)
				#print "len(inSurfGrid[lev])", len(inSurfGrid[lev])
				#print "len(inSurfGrid[lev][xx])", len(inSurfGrid[lev][xx])
				sid = inSurfGrid[lev][xx][yy]
				if sid == None:
					tidPosGridThisLev[xx][yy] = -1
				elif sid in sidSet:
					tidPosGridThisLev[xx][yy] = sidToTidPos[lev][sid]
					maxTid = max(maxTid, tidPosGridThisLev[xx][yy])
				else:
					tidPosGridThisLev[xx][yy] = 0
		tidPosGrid.append(tidPosGridThisLev)
	
	return tidPosGrid




