#!/usr/bin/python
import pygame, math, ut, os, pprint, sys, random, time, shutil, glob
import cPickle as pickle
# OpenCl stuff!
import pyopencl as cl
import numpy as np
from PIL import Image

#this line would create a context
cntxt = cl.create_some_context()
#now create a command queue in the context
queue = cl.CommandQueue(cntxt)

outFile = "/tmp/out"

black = (0, 0, 0)
grey = (.3, .3, .3)
white = (1, 1, 1)
red =	(1, 0, 0)
green = (0, 1, 0)
blue =	(0, 0, 1)
yellow =(1, 1, 0)
cyan = (0, 1, 1)
magenta =(1, 0, 1)

rYellow =(1, .5, 0)
gYellow =(.5, 1, 0)
gCyan = (0, 1, .5)
bCyan = (0, .5, 1)
rMagenta =(1, 0, .5)
bMagenta =(.5, 0, 1)

lRed =	(1, .5, .5)
lGreen = (.5, 1, .5)
lBlue =	(.5, .5, 1)
lYellow =(1, 1, .5)
lCyan = (.5, 1, 1)
lMagenta =(1, .5, 1)



clrs = [
red,	 # 0
green,   # 1
blue,	# 2
yellow,  # 3
cyan,	# 4
magenta, # 5
white,   # 6
rYellow, # 7
gYellow, # 8
gCyan,   # 9
bCyan,   # 10
rMagenta,# 11
bMagenta,# 12
grey,	# 13
lRed,	# 14
lGreen,  # 15
lBlue,   # 16
lYellow, # 17
lCyan,   # 18
lMagenta # 19
]

clrsInt = []
for clr in clrs:
	clrInt = []
	for f in clr:
		clrInt.append(int(255*f))
	clrsInt.append(clrInt)

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


def vX255(v):
	ret = [f*255 for f in v]
	if type(v) == type(()):
		ret = tuple(ret)
	return ret


def vBy255(v):
	ret = [float(f)/255 for f in v]
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
	levThreshRemap = ut.gamma(levThresh, warpUi.parmDic("gamma"))

	levRel = float(lev)/(nLevels-1)
	minThreshThisLev = ut.mix(minThreshMin, minThreshMax, levRel)
	maxThreshThisLev = ut.mix(maxThreshMin, maxThreshMax, levRel)


	levThreshRemap = ut.mix(minThreshThisLev, maxThreshThisLev, levThreshRemap)
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

		levThreshArray = np.array(levThreshInt, dtype=np.uint8)
		levThreshArray_buf = cl.Buffer(cntxt, cl.mem_flags.READ_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=levThreshArray)
		
		imgArray = np.array(list(pygame.surfarray.array3d(img)))
		imgArray_buf = cl.Buffer(cntxt, cl.mem_flags.READ_ONLY |
		cl.mem_flags.COPY_HOST_PTR,hostbuf=imgArray)
		
		jtCons = np.empty((nLevels, res[0], res[1]), dtype=np.intc)
		jtCons.fill(0)

		jtConsThisLev = np.empty((res[0], res[1]), dtype=np.intc)
		jtConsThisLev.fill(0)
		jtConsThisLev_buf = cl.Buffer(cntxt, cl.mem_flags.WRITE_ONLY, jtConsThisLev.nbytes)
		
		
		kernelPath = ut.projDir + "/GPUKernel.c"
		with open(kernelPath) as f:
			kernel = "".join(f.readlines()) % (res[1], res[0])
		#int index = rowid * ncols * npix + colid * npix;
		# build the Kernel
		for lev in range(nLevels):
			bld = cl.Program(cntxt, kernel).build()
			launch = bld.initJtC(
					queue,
					imgArray.shape,
					None,
					np.int32(warpUi.parmDic("nLevels")),
					np.int32(lev),
					imgArray_buf,
					levThreshArray_buf,
					jtConsThisLev_buf)
			launch.wait()


			cl.enqueue_read_buffer(queue, jtConsThisLev_buf, jtConsThisLev).wait()
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
	renSeqDir = "/".join(renPath.split("/")[:-1])
	ut.mkDirSafe(renSeqDir)

	ut.timerStop(warpUi, "initJtGridXYLoop")

	return jtGrid, tholds

def setAOV(warpUi, name, dbImgDic, lev, nLevels, x, y, val):
	prevVal = black
	aovParmName = "aov_" + name	
	if aovParmName in warpUi.parmDic.parmDic.keys() and warpUi.parmDic(aovParmName) == 1 and lev <= len(dbImgDic[name]): # TODO: Won't last cond always be true?
		res = dbImgDic[name][lev].get_size()
		if x < res[0] and y < res[1]:
			#prevVal = dbImgDic[name][lev].get_at((x,y))
			newVal = tuple(list(val))
			newVal = ut.clampVSc(newVal, 0, 255)
			dbImgDic[name][lev].set_at((x,y), newVal)
			dbImgDic[name][nLevels].set_at((x,y), newVal)

def intToClr(i):
	return vX255(clrs[i%len(clrs)])


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

def loadLatestTidToSids(warpUi):
	print "_loadLatestTidToSids(): BEGIN - finding last tidToSidsFile."
	lastFramePath = getLastFrameDirPath(warpUi)
	tidToSidsPath = lastFramePath + "/tidToSids"
	print "_loadLatestTidToSids(): attempting to load", tidToSidsPath, "..."
	if os.path.exists(tidToSidsPath):
		print "_loadLatestTidToSids(): Found, pickleLoad-ing..."
	if os.path.exists(tidToSidsPath):
		warpUi.tidToSids = pickleLoad(tidToSidsPath)
	else:
		print "_loadLatestTidToSids(): Not found, setting to None."
		warpUi.tidToSids = None

def growCurves(warpUi, jtGrid, frameDir):
	print "\n_growCurves(): growing curves for", frameDir
	nLevels = warpUi.parmDic("nLevels")
	nCurves = 0
	res = (len(jtGrid), len(jtGrid[0]))
	
	if warpUi.tidToSids == None:
		loadLatestTidToSids(warpUi)
		if warpUi.tidToSids == None:
			warpUi.tidToSids = [{} for i in range(nLevels)]
	if warpUi.sidToTid == None:
		warpUi.sidToTid = [{} for i in range(nLevels)]


	# inHoles delimit holes; inSurfs do not.
	curToPrevSidDic = [{} for i in range(nLevels)]
	surfs = [[] for i in range(nLevels)]
	inHoles = [[] for i in range(nLevels)]
	inSurfs = [[] for i in range(nLevels)]
	inSurfNow = [False for i in range(nLevels)]
	curves = [[] for i in range(nLevels)]
	#sidToCurves = [{}] * nLevels

	inSurfGrid = [[[None for yy in range(res[1])] for xx in range(res[0])] for lev in range(nLevels)]

	imgJtInOut = pygame.Surface(res)
	dbImgs = ["inSurfNow", "surfsAndHoles", "inPrev", "cid", "cvSid", "cidPost", "sid", "sidPost"]
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
						cvClr = intToClr(jt.cv.cid)
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
						if jt.cons[0][1] == -1:
							imgJtInOut.set_at((x, y), (255, 0, 0))
						else:
							imgJtInOut.set_at((x, y), (0, 255, 0))
						imgJtInOut.set_at((x, y), vX255(clrs[jt.cv.cid%len(clrs)]))

						inSurfNow[lev] = not inSurfNow[lev]
						# NOTE: inHoles and inSurfs are arrays because you can be inside multiple 
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
					inSurfGrid[lev][x][y] = currentSid
					if not (warpUi.inSurfGridPrev == None or
						# I THINK below avoids overlapping start of cyc with end of prev
						(not math.floor(warpUi.getOfsWLev(lev)) ==
							math.floor(warpUi.getOfsWLev(lev, warpUi.parmDic("fr")-1)))) : # NOTE:  this is apparently NOT the same as "if warpUi.inSurfGridPrev:"
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
			sfClr = intToClr(jt.cv.surf.sid)
			while True:
				xx, yy = jt.xy
				setAOV(warpUi, "cvSid", dbImgDic, lev, nLevels, xx, yy, sfClr)
				sfClr = intToClr(jt.cv.cid)
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
					warpUi.tidToSids[lev][sidToMergeTo] = {"sids":set([sid])}
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
			elif not sid in warpUi.sidToTid[lev].keys(): # Make sure this sid isn't already in a tid.
				# This sid will not be merged, it will be a tid.
				if sid in warpUi.tidToSids[lev].keys():
					warpUi.tidToSids[lev][sid]["sids"].add(sid)
				else:
					warpUi.tidToSids[lev][sid] = {"sids" : set([sid])}

		# Translate tidToSids to sidToTid.
		# TODO: Is this really what this does?
		# TODO: When you do checkpointing, this is where you del tids > frPerCycle old

		for tid,sidData in warpUi.tidToSids[lev].items():
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
						inSurfGrid[lev][x][y] = sidNew
					else:
						sidNew = sidOld
					#setAOV(warpUi, "sidPost", dbImgDic, lev, nLevels, x, y, intToClr(sidNew))
	
	# Set sidPost AOV using GPU
	print "_growCurves(): drawing sidPost AOV using GPU..."
	# Mark dirty before GPU ops in case of crash.
	ut.indicateProjDirtyAs(warpUi, True, "saveSidPostGPU_inProgress")
	
	kernel = """
void setArrayCell(int x, int y, int xres,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * 3 + x * 3;
	ret[i] = val[0];
	ret[i+1] = val[1];
	ret[i+2] = val[2];
}

int getCellScalar(int x, int y, int xres,
  int __attribute__((address_space(1)))* inSurfGrid)
{
	int i = y * xres + x;
	return inSurfGrid[i];
}

__kernel void setSidPostAr(
			int xres,
			int nClrs,
			__global int* inSurfGrid,
			__global uchar* clrsInt,
			__global uchar* sidPostThisAr,
			__global uchar* sidPostALL)
{
	int x = get_global_id(1);
	int y = get_global_id(0);

	int sid = getCellScalar(x, y, xres, inSurfGrid);
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
		inSurfGridAr_buf = cl.Buffer(cntxt, cl.mem_flags.READ_ONLY |
			cl.mem_flags.COPY_HOST_PTR,hostbuf=inSurfGridAr)

		if lev == 0:
			sidPostALL = np.zeros(inSurfGridAr.shape + (3,), dtype=np.uint8)
			sidPostALL_buf = cl.Buffer(cntxt, cl.mem_flags.WRITE_ONLY |
				cl.mem_flags.COPY_HOST_PTR,hostbuf=sidPostALL)

		clrsIntAr = np.array(clrsInt, dtype=np.uint8)
		clrsIntAr_buf = cl.Buffer(cntxt, cl.mem_flags.READ_ONLY |
			cl.mem_flags.COPY_HOST_PTR,hostbuf=clrsIntAr)

		sidPostThisLev = np.zeros(inSurfGridAr.shape + (3,), dtype=np.uint8)
		sidPostThisLev_buf = cl.Buffer(cntxt, cl.mem_flags.WRITE_ONLY,
			sidPostThisLev.nbytes)

		bld = cl.Program(cntxt, kernel).build()
		launch = bld.setSidPostAr(
				queue,
				inSurfGridAr.shape,
				None,
				np.int32(res[1]),
				np.int32(len(clrsInt)),
				inSurfGridAr_buf,
				clrsIntAr_buf,
				sidPostThisLev_buf,
				sidPostALL_buf)
		launch.wait()

		cl.enqueue_read_buffer(queue, sidPostThisLev_buf, sidPostThisLev).wait()
		cl.enqueue_read_buffer(queue, sidPostALL_buf, sidPostALL).wait()

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
		#	drawBbx(warpUi, sidToCvs[lev][sid]["bbx"], "sid", dbImgDic, lev, nLevels, intToClr(sid))
		#for tid, turfData in warpUi.tidToSids[lev].items():
		#	if "bbx" in turfData.keys(): # TODO should bbx always be in turfData.keys()?
		#		drawBbx(warpUi, turfData["bbx"], "sid", dbImgDic, lev, nLevels, intToClr(tid))
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

	ut.timerStop(warpUi, "growC_save")
	return inSurfGrid, sidToCvs

	#-- END OF growCurves(warpUi, jtGrid, frameDir):


def writeTidImg(warpUi, inSurfGrid):
	print "\n_writeTidImg(): BEGIN"
	res = (len(inSurfGrid[0]), len(inSurfGrid[0][0]))
	nLevels = warpUi.parmDic("nLevels")
	dbImgDic = {}
	dbImgDic["tid"] = [pygame.Surface(res) for i in range(nLevels+1)][:]
	allTids = set()
	for y in range(res[1]):
		print "_writeTidImg(), y=", y
		for x in range(res[0]):
			for lev in range(nLevels):
				sid = inSurfGrid[lev][x][y]
				if not sid == None:
					if sid in warpUi.sidToTid[lev].keys():
						tid = warpUi.sidToTid[lev][sid]
						if lev == 0: allTids.add(tid)
						setAOV(warpUi, "tid", dbImgDic, lev, nLevels, x, y, intToClr(tid))
	allTidsLs = list(allTids)
	allTidsLs.sort()

	for lev in range(nLevels+1):
		levStr = "ALL" if lev == nLevels else "lev%02d" % lev
		levDir,imgPath = warpUi.getDebugDirAndImg("tid", levStr)
		ut.mkDirSafe(levDir)
		print "_writeTidImg(): imgPath", imgPath
		pygame.image.save(dbImgDic["tid"][lev], imgPath)
	print "\n_writeTidImg(): END"

def genDataWrapper(warpUi):
	genDataStartTime = time.time()

	img = pygame.image.load(warpUi.images["source"]["path"])
	border(img)

	# Make required dirs.
	fr, frameDir = warpUi.makeFramesDataDir()

	# Load prev inSurfGrid.
	inSurfGridPrev = None
	frameDirPrev = warpUi.framesDataDir + ("/%05d" % (fr-1))

	jtGrid, tholds = initJtGrid(img, warpUi)

	ut.timerStart(warpUi, "growCurves")
	inSurfGrid, sidToCvs = growCurves(warpUi, jtGrid, frameDir)
	ut.timerStop(warpUi, "growCurves")
	# TODO: TEMP - this should be done in warp.py when genData is stopped...?
	print "\n\n_genData(): ----- doing pickleDump(" + frameDir + "/inSurfGrid"
	pickleDump(frameDir + "/inSurfGrid", inSurfGrid)

	frameDirLs = frameDir.split("/")
	prevFr = int(frameDirLs[-1]) - 1
	frameDirLs[-1] = "%05d" % prevFr
	prevFrInSurfGrid = "/".join(frameDirLs) + "/inSurfGrid"
	print "\n\n\n_genData(): prevFrInSurfGrid:", prevFrInSurfGrid, "\n\n"


	warpUi.inSurfGridPrev = inSurfGrid[:]


	# Save inSurfGrid
	sidToCvDic = convertCvDicToDic(sidToCvs, warpUi)
	pickleDump(frameDir + "/sidToCvDic", sidToCvDic)
	pickleDump(frameDir + "/tholds", tholds)

	# Save sidToCvs for this frame.

	if fr % warpUi.parmDic("backupDataEvery") == 0:
		print "_genData(): BACKING UP tidToSids:"
		#shutil.copy2(warpUi.seqDataVDir + "/tidToSids", frameDir)
		#pickleDump(frameDir + "/tidToSids", warpUi.tidToSids)
		#ut.exeCmd("cp " + warpUi.seqDataVDir + "/tidToSids " + frameDir)
	#if fr % backupDataEvery == 1:
	#	print "_genData(): NOT deleting", prevFrInSurfGrid
	#else:
	#	print "_genData(): deleting", prevFrInSurfGrid
	#	ut.safeRemove(prevFrInSurfGrid)

	#pickleDump(warpUi.seqDataVDir + "/sidToTid", warpUi.sidToTid) search->MARK_A!!!

	# Record stats
	genDataStopTime = time.time() - genDataStartTime
	memUsage = ut.recordMemUsage(frameDir + "/memUsage")

	statStr = "Time: %.2f seconds\nMemory: %.2f%%\n" % (genDataStopTime, memUsage)
	with open(frameDir + "/stats", 'w') as f:
		f.write(statStr)


def saveTidToSids(warpUi):
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


	sidToCvs = {}

	if warpUi.genRen1fr == 1:
		warpUi.flushDics()
		genDataWrapper(warpUi)
		renCvWrapper(warpUi)
		frameDir = getLastFrameDirPath(warpUi)
		saveTidToSids(warpUi)
	elif warpUi.parmDic("doRenCv") == 1:
		renCvWrapper(warpUi)
	else:
		genDataWrapper(warpUi)
		if warpUi.parmDic("fr") % warpUi.parmDic("backupDataEvery") == 0:
			saveTidToSids(warpUi)
		#pickleDump(frameDir + "/tidToSids", warpUi.tidToSids)

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

def renCvWrapper(warpUi):
	print "_renCvWrapper(): BEGIN"
	fr, frameDir = warpUi.makeFramesDataDir(doMake=False)
	frPerCycle = warpUi.parmDic("frPerCycle")
	backupDataEvery = warpUi.parmDic("backupDataEvery")
	# Load tidToSids when you don't have one, or every frPerCycle frames.
	if warpUi.tidToSids == None:
		print "_renCvWrapper(): warpUi.tidToSids == None"
	else:
		print "_renCvWrapper(): warpUi.tidToSids NOT == None"
	if warpUi.tidToSids == None or fr == warpUi.parmDic("frStart") \
			or fr % backupDataEvery == 0:
		print "_renCvWrapper(): Updating tidToSids"
		framesDir = warpUi.seqDataVDir + "/frames"
		nextSafeTidFr = fr + frPerCycle # ensure all tids have been merged.
		frToLoad = backupDataEvery*int(math.ceil(
			float(nextSafeTidFr)/backupDataEvery)) # next fr that has backup.
		dicPathToLoad = warpUi.seqDataVDir + ("/frames/%05d/tidToSids" % frToLoad)

		if os.path.exists(dicPathToLoad):
			print "_renCvWrapper(): loading dicPathToLoad..."
			warpUi.tidToSids = pickleLoad(dicPathToLoad)
		else:
			print "_renCvWrapper(): dicPathToLoad not found, attempting to load latest..."
			loadLatestTidToSids(warpUi)
	#else:
	#	loadLatestTidToSids(warpUi)
	# MAY USE LATER # if warpUi.tidToSids == None or frForTid % backupDataEvery == 1:

	# MAY USE LATER #	frForTid = fr + warpUi.parmDic("frPerCycle")
	# MAY USE LATER #	# Get the checkpoint after fr + frPerCycle.
	# MAY USE LATER #	tidToSidsFr = backupDataEvery*(1 + frForTid/backupDataEvery)
	# MAY USE LATER #	dud, tidToSidsDir = warpUi.makeFramesDataDir(tidToSidsFr, False)
	# MAY USE LATER #	# Get next checkpoint backup.
	# MAY USE LATER #	tidToSidsFile = tidToSidsDir + "/tidToSids"
	# MAY USE LATER #	print "_renCvWrapper(): checking for", tidToSidsFile
	# MAY USE LATER #	if not os.path.exists(tidToSidsFile):
			
	# TODO is below necessary?  Why was it ever un-commented?  As well as MARK_A
	#if warpUi.sidToTid == None:
	#	warpUi.sidToTid = pickleLoad(warpUi.seqDataVDir  + "/sidToTid")
	sidToCvDic = pickleLoad(frameDir + "/sidToCvDic")
	tholds = pickleLoad(frameDir + "/tholds")
	if sidToCvDic == None:
		if warpUi.parmDic("anim") == 1:
			warpUi.animButCmd()
		warpUi.setStatus("error", "ERROR: sidToCvDic == None")
	else:
		renCv(warpUi, sidToCvDic, tholds)
	print "_renCvWrapper(): END"



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
	return min(1, 2*ut.smoothstep(progStart, progEnd, level))

def calcXf(warpUi, prog, res, relSize, bbx):
	fall = prog * res[1] * warpUi.parmDic("fallDist")
	# Slower for biggekr
	relSizeF = relSize[0]*relSize[1]
	resF = res[0]*res[1]
	#rels = float(relSizeF)/(resF)
	rels = relSizeF
	#rels = .5
	
	relsPostSmooth = ut.smoothstep(0, warpUi.parmDic("fallUseAsBiggest"), rels)
	relsPostSmooth = pow(relsPostSmooth, warpUi.parmDic("fallBiggestPow"))
	
	fallK = ut.mix(1.0, warpUi.parmDic("fallKForBiggest"), relsPostSmooth)

	fall *= fallK

	if warpUi.parmDic("fallMode") == "orig":
		bbxCent = ((bbx[0][0]+bbx[1][0])/2, (bbx[0][1]+bbx[1][1])/2)
		origin = (res[0]*warpUi.parmDic("fallVecX"), res[1]*warpUi.parmDic("fallVecY"))
		fallDir = ut.vDiff(origin, bbxCent)
		#fallDir[1] *= warpUi.parmDic("fallYscale")
		#fallDir = (100, 100)
		tx = int(fall * fallDir[0]/res[0])
		ty = int(fall * fallDir[1]/res[1])
	elif warpUi.parmDic("fallMode") == "xline":
		bbxCent = (bbx[0][1]+bbx[1][1])/2
		origin = res[1]*warpUi.parmDic("fallVecX")
		fallDir = bbxCent - origin
		tx = 0
		ty = int(fall * fallDir/res[1])
	elif warpUi.parmDic("fallMode") == "yline":
		bbxCent = (bbx[0][0]+bbx[1][0])/2
		origin = res[0]*warpUi.parmDic("fallVecX") #TODO THAT SHOULD BE Y!!!
		fallDir = bbxCent - origin
		tx = int(fall * fallDir/res[0])
		ty = 0
	else:
		tx = 0
		ty = int(fall)

	return tx, ty

def setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, jy, tx, ty, tidRanClr, k, alpha, iJt=None):
	texClr = srcImg.get_at((jx, jy))
	texClr = list(texClr)[:3]
	cTripPow = 3
	mixClr = ut.mix(warpUi.parmDic("mixClrSob"),
		warpUi.parmDic("mixClrTrp"), pow(prog, cTripPow))
	clr = ut.mixV(texClr, tidRanClr, mixClr)
	clr = ut.multVSc(clr, k)

	# Adapted from  setAOV(warpUi, "ren", outputs, lev, nLevels, jx + tx, jy + ty, clr)
	thisDic = outputs["ren"]
	prevVal = black
	jxt = jx + tx
	jyt = jy + ty
	if lev <= len(thisDic): # TODO: Won't this always be true?
		res = thisDic[lev].get_size()
		if jxt < res[0] and jxt > -1 and jyt < res[1] and jyt > -1:

			# Write UNPREMULTIPLIED color to this level AOV
			if warpUi.parmDic("aov_perLev") == 1:
				newValThisLev = tuple(ut.multVSc(clr, alpha))
				newValThisLev = ut.clampVSc(newValThisLev, 0, 255)
				#newValThisLev = tuple(clr)
				thisDic[lev].set_at((jxt,jyt), newValThisLev)

			newVal = tuple(list(clr) + [255])

			db = False
			if not db or iJt == None:
				# Comp for ALL level
				prevVal = thisDic[nLevels].get_at((jxt,jyt))
				occludePrev = .75 # TODO Parm?
				prevVal = ut.mixV(prevVal,
					ut.multVSc(prevVal, (1-alpha)), occludePrev)


				newVal = ut.vAdd(prevVal, ut.multVSc(newVal, alpha))
				newValLs = []
				for v in newVal:
					newValLs.append(int(v))
				newVal = tuple(newValLs)
				newVal = ut.clampVSc(newVal, 0, 255)
			else: # DEBUG: show curve prog 
  				cProg = float(iJt % 20)/19*255
  				newVal = (255-cProg,cProg, 0, 255)
  				if iJt < 4:
					newVal = (255-cProg,cProg, 255, 255)

			thisDic[nLevels].set_at((jxt,jyt), newVal)



	

def renSid(warpUi, srcImg, tid, sid, nLevels, lev, level, levelAlph, res, sidToCvDic, outputs, bbx, bbxSize, relSize, thold, falseArray):
	tidRanClr = intToClr(sid)


	prog = calcProg(warpUi, tid, level, lev)
	tx,ty = calcXf(warpUi, prog, res, relSize, bbx)
	#tx,ty = (0, 0)

	# TODO: You don't have to include the whole sidToCvDic, just sidToCvDic[lev]
	cvs = sidToCvDic[lev][sid]["cvs"]
	allCoords = []

	for cv in cvs: # TODO: Delete this, and "False" part below
		allCoords += cv

	for cv in cvs:
		iJt = 0
		while iJt < len(cv):
			jt = cv[iJt]
			jtNext = cv[(iJt+1) % len(cv)]
			jtPrev = cv[(iJt-1) % len(cv)]
			jx,jy = list(jt)

			#surfAlpha = levelAlph * (1-prog)
			sfFdIn = .2
			sfFdOut = .3
			sfA = warpUi.parmDic("sfA")
			sfK = warpUi.parmDic("sfK")
			surfAlpha = sfA * levelAlph * ut.smoothpulse(0, sfFdIn, 1-sfFdOut, 1, prog)
			cvFdIn = .1
			cvFdOut = .1
			cvA = warpUi.parmDic("cvA")
			cvK = warpUi.parmDic("cvK")
			curveAlpha = cvA * levelAlph * ut.smoothpulse(0, cvFdIn, 1-cvFdOut, 1, prog)


			if jx > jtPrev[0]:
				# Skip to the top (lowest #) of a vertical line
				while (jtNext[0] == jx	# next x is same - vertical line
						and jtNext[1] < jy):   # next y is lower
					iJt += 1
					jx,jy = list(cv[iJt])
					jtNext = cv[(iJt+1) % len(cv)]
					setRenCvFromTex(warpUi, prog, srcImg, outputs, lev,
						nLevels, jx, jy, tx, ty, tidRanClr, cvK, curveAlpha, iJt)
				if jtNext[0] < jx:
					# If the next x is less than this x -- which I think 
					# would only happen if the above while loop landed us
					# at a back-curving turn - skip this jt.
					# TODO: must this next line exist?
					setRenCvFromTex(warpUi, prog, srcImg, outputs, lev,
						nLevels, jx, jy, tx, ty, tidRanClr, cvK, curveAlpha, iJt)
					iJt += 1
					continue

				#yy = jy +1

				# MAIN FILLING - Draw vertical line up to next curve in this sid.
				yy = jy
				while (int(avgLs(srcImg.get_at((jx,yy))[:-1])) > thold*255) and yy > 0:
					setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, yy, tx, ty, tidRanClr, sfK, surfAlpha)
					yy -= 1


			# Draw the curve. 
			setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, jy, tx, ty, tidRanClr, cvK, curveAlpha, iJt)

			iJt += 1



def renCv(warpUi, sidToCvDic, tholds):
	
	print "\n\n\n"
	print "_renCv(): *******************"
	print "_renCv(): *** DOING renCv ***"
	print "_renCv(): *******************"

	warpUi.setStatus("busy", "Doing renCv...")

	res = warpUi.res
	nLevels = warpUi.parmDic("nLevels")


	outputs = {}
	srcImg = pygame.image.load(warpUi.images["source"]["path"])
	# TODO can you reuse srcImg for srcImgRenCv without referencing/modifying it?
	srcImgRenCv = pygame.image.load(warpUi.images["source"]["path"])

	dark = pygame.Surface((srcImgRenCv.get_width(), srcImgRenCv.get_height()), flags=pygame.SRCALPHA)
	dark.fill((50, 50, 50, 0))
	srcImgRenCv.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

	renOutputsMultiLev = ["ren"]
	for name in renOutputsMultiLev:
		# TODO are those [:]s necessary?
		outputs[name] = [pygame.Surface(res) for i in range(nLevels+1)][:]

	renOutputsOneLev = ["move"]
	for name in renOutputsOneLev:
		outputs[name] = pygame.Surface(res)


	renMov = False #TODO: make this a parm obv
	if renMov:
		ut.timerStart(warpUi, "moveImg")
		# Visualize movement
		circleSizeRel = .1
		circleSize = circleSizeRel * max(res[0],res[1])
		for x in range(res[0]):
			for y in range(res[1]):
				c = srcImgRenCv.get_at((x, y))
				c = list(c)[:3]
				c.reverse() # TODO/NOTE: Stupid fucking bug or something requires this reverse.
				lum = int(ut.vAvg(c))
				origin = (res[0]*warpUi.parmDic("fallVecX"), res[1]*warpUi.parmDic("fallVecY"))
				dist = ut.vDist(origin, (x,y))
				c[0] = 0 if dist > circleSize else 255
				c[1] = lum
				c[2] = lum
				newVal = tuple(list(c) + [255])
				outputs["move"].set_at((x,y), newVal)
		ut.timerStop(warpUi, "moveImg")



	# Sort levels in order of tholds (thresholds).
	levLs = range(nLevels)
	tholdsAndLevLs = zip(tholds, levLs)
	tholdsAndLevLs.sort()
	dud, levsSortedByTholds = zip(*tholdsAndLevLs)

	print "\n\n_renCv(): tholds:", tholds
	print "_renCv(): levsSortedByTholds:", levsSortedByTholds


	falseArray = [[False for y in range(res[1])] for x in range(res[0])] 
	for thold, lev in tholdsAndLevLs[warpUi.parmDic("startLev"):]:
		tids = warpUi.tidToSids[lev].keys()
		iTid = 0
		nTids = len(tids)
		print "_renCv(): lev:", lev, "thold:", thold, "nTids:", nTids
		for tid in tids:
			iTid += 1
			print "\r\ttid:", tid, ("(%d of %d)" % (iTid, nTids)), "sids:",
			sids = warpUi.tidToSids[lev][tid]["sids"]

			levProg = warpUi.getOfsWLev(lev) % 1.0

			# Fade in and out - TODO: Improve this
			levelAlph = levProg* (1-levProg)**2
			levelAlph = min(levProg*1.5*pow(thold,.5), 1)
			levelAlph = float(lev)/(nLevels-1)
			levelAlph = levelAlph**.1
			levelAlph = 1 #TEMP?

			iSid = 0
			for sid in sids:
				if sid in sidToCvDic[lev]:
					bbx = sidToCvDic[lev][sid]["bbx"]
					bbxSize = [bbx[1][0] - bbx[0][0], bbx[1][1] - bbx[0][1]]
					relSize = [float(bbxSize[0])/res[0], float(bbxSize[1])/res[1]]
					iSid += 1
					print sid,
					#print "bbx:", bbx, "relSize:", relSize,
					# Try only ren sids <= half res
					maxSize = warpUi.parmDic("maxSize")
					#print "\n\n yyyyyyy sid", sid, "bbx", bbx, "bbxSize", bbxSize, "res", res, "relSize", relSize
					if relSize[0] <= maxSize and relSize[1] <= maxSize:
						renSid(warpUi, srcImg, tid, sid, nLevels, lev, levProg, levelAlph, res, sidToCvDic, outputs, bbx, bbxSize, relSize, thold, falseArray)
		print




	for name in renOutputsMultiLev:
		for lev in range(nLevels+1):
			levStr = "ALL" if lev == nLevels else "lev%02d" % lev
			levDir,imgPath = warpUi.getRenDirAndImgPath(name, levStr)
			ut.mkDirSafe(levDir)
			if name == "ren" and lev == nLevels:
				print "\n\n**********************************************"
				print "\n\n_renCv(): ***** Saving", name, " image, path:", imgPath, "\n\n"
				print "**********************************************\n\n"
			else:
				print "_renCv(): Saving", name, " image, path:", imgPath
			pygame.image.save(outputs[name][lev], imgPath)
			# Save bmp
			if False:
				bmpPath = imgPath.replace(warpUi.seqImgExt, ".bmp")
				pygame.image.save(outputs[name][lev], bmpPath)
				#ut.exeCmd("convert -resize 400% " + bmpPath + " " + bmpPath)

	for name in renOutputsOneLev:
		levDir,imgPath = warpUi.getRenDirAndImgPath(name)
		ut.mkDirSafe(levDir)
		print "_renCv(): Saving", name, " image, path:", imgPath
		pygame.image.save(outputs[name], imgPath)
		ut.exeCmd("convert -resize 200% " + imgPath + " " + imgPath)

	print "_renCv(): done renCv for fr", warpUi.parmDic("fr")



