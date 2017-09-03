#!/usr/bin/python
import pygame, math, ut, pickle, os, pprint, sys, random, time

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

neighboursToConns = {
	(0, 0,\
	 0, 0):[],

	(0, 0,\
	 0, 1):[((0, 1), (1, 0))],

	(0, 0,\
	 1, 0):[((-1, 0), (0, 1))],

	(0, 0,\
	 1, 1):[((-1, 0), (1, 0))],

	(0, 1,\
	 0, 0):[((1, 0), (0, -1))],

	(0, 1,\
	 0, 1):[((0, 1), (0, -1))],

	(0, 1,\
	 1, 0):[((-1, 0), (0, 1)), ((1, 0), (0, -1))],

	(0, 1,\
	 1, 1):[((-1, 0), (0, -1))],

	(1, 0,\
	 0, 0):[((0, -1), (-1, 0))],

	(1, 0,\
	 0, 1):[((0, 1), (1, 0)), ((0, -1), (-1, 0))],

	(1, 0,\
	 1, 0):[((0, -1), (0, 1))],

	(1, 0,\
	 1, 1):[((0, -1), (1, 0))],

	(1, 1,\
	 0, 0):[((1, 0), (-1, 0))],

	(1, 1,\
	 0, 1):[((0, 1), (-1, 0))],

	(1, 1,\
	 1, 0):[((1, 0), (0, 1))],

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
	nbrs = None
	jid = None
	nx = None
	pv = None
	cv = None

	def __init__(self, xy, level, texClr, cons, jid, nbrs=None):
		self.xy = xy
		self.level = level
		self.texClr = texClr
		self.cons = cons
		self.jid = jid
		self.nbrs = nbrs

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
	#print "pOut: printing to", outFile, ":", ret
	with open(outFile, "a") as f:
		f.write(ret)
	#os.system("echo " + ret + " >> " + outFile)
	return ret

	

	

def pickleDump(filePath, data):
	print "Pickle dumping", filePath, "..."
	with open(filePath, 'w') as dataFile:
		pickle.dump(data, dataFile)
	print "\tDone pickle dumping", filePath

def pickleLoad(filePath):
	print "Pickle loading", filePath, "..."
	
	if os.path.exists(filePath):
		with open(filePath, 'r') as dataFile:
			ret = pickle.load(dataFile)
	else:
		print "ERROR: file not found!"
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


def gridToImgV(grid):
	res = (len(grid), len(grid[0]))
	ret = pygame.Surface(res)
	for x in range(res[0]):
		for y in range(res[1]):
			v = ut.multVSc(grid[x][y], 255)
			v = ut.clampVSc(v, 0, 255)
			ret.set_at((x, y), (v[0], v[1], v[2], 255))
	return ret



def heatMap(v, parmDic):
	cDark = parmDic("cDark")
	cMid = parmDic("cMid")
	cLight = parmDic("cLight")
	if v < .5:
		return ut.mixV(cDark, cMid, v/.5)
	else:
		return ut.mixV(cMid, cLight, (v-.5)/.5)

def vecToClr(v):
	ret = []
	for i in v:
		ret.append(int(ut.clamp(int(i*255), 0, 255)))
	ret += [255]
	return tuple(ret)

def getLevThresh(warpUi, lev, nLevels):
	minThreshMin = warpUi.parmDic("minThresh")
	maxThreshMax = warpUi.parmDic("maxThresh")
	rangeThresh = warpUi.parmDic("rangeThresh")
	minThreshMax = ut.mix(minThreshMin, maxThreshMax, 1-rangeThresh)
	maxThreshMin = ut.mix(minThreshMin, maxThreshMax, rangeThresh)

	levThresh = warpUi.getOfsWLev(lev) % 1.0
	levThreshRemap = ut.gamma(levThresh, warpUi.parmDic("gamma"))

	levProg = float(lev)/(nLevels-1)
	minThreshThisLev = ut.mix(minThreshMin, minThreshMax, levProg)
	maxThreshThisLev = ut.mix(maxThreshMin, maxThreshMax, levProg)


	#levThreshRemap = ut.mix(warpUi.parmDic("minThresh"), warpUi.parmDic("maxThresh"), levThreshRemap)
	levThreshRemap = ut.mix(minThreshThisLev, maxThreshThisLev, levThreshRemap)
	levThreshInt = int(levThreshRemap*255)
	return levThreshRemap, levThreshInt




def initJtGrid(img, warpUi):
	print "In initJtGrid..."
	ofs = warpUi.parmDic("ofs")
	nLevels = warpUi.parmDic("nLevels")
	kSurf = warpUi.parmDic("kSurf")
	res = img.get_size()
	nJoints = 0
	jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
	tholds = [None for lev in range(nLevels)]
	
	ut.timerStart(warpUi, "initJtGridXYLoop")
	for x in range(res[0]-1):
		for y in range(res[1]-1):
			# TODO: I 'spect you should do lev loop first, then x,y so you can do all per-lev calcs once.
			intens = float(avgLs(img.get_at((x,y))[:-1]))/255
			thisLev = math.ceil(nLevels*(-ofs/nLevels + intens))
			vFlt = float(thisLev+ofs)/nLevels
			hm = heatMap(vFlt, warpUi.parmDic)
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
						jtGrid[x][y][lev] =  [joint((x,y), levThreshRemap, texClr, cons[0], nJoints, nbrs),
											   joint((x,y), levThreshRemap, texClr, cons[1], nJoints + 1, nbrs),]
						nJoints += 2
					else:
						jtGrid[x][y][lev] = [joint((x,y), levThreshRemap, texClr, cons[0], nJoints, nbrs)]
						nJoints += 1
	# Write stats
	ut.timerStop(warpUi, "initJtGridXYLoop")

	#warpUi.gridJt = jtGrid[:]
	renPath = warpUi.images["ren"]["path"]
	renSeqDir = "/".join(renPath.split("/")[:-1])
	ut.mkDirSafe(renSeqDir)
	#print "SAVING RENDERED IMAGE:", renPath


	return jtGrid, tholds

def setAOV(warpUi, name, dbImgDic, lev, nLevels, x, y, val):
	prevVal = black
	aovParmName = "aov_" + name	
	#print ("_setAOV: aovParmName", aovParmName, ", aovParmName in keys:", aovParmName in warpUi.parmDic.parmDic.keys(), ", warpUi.parmDic(aovParmName):", warpUi.parmDic(aovParmName))
	#print "_setAOV: lev <= len(dbImgDic[name])", lev <= len(dbImgDic[name])
	if aovParmName in warpUi.parmDic.parmDic.keys() and warpUi.parmDic(aovParmName) == 1 and lev <= len(dbImgDic[name]): # TODO: Won't last cond always be true?
		#print ("_setAOV: DOING", aovParmName)
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
	#print "\n\n\n=========== }}}}}}}}}} cv.bbx", cv.bbx
	# Vertical lines
	for xx in range(xmn, xmx):
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xx, ymn, clr)
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xx, ymx, clr)
	# Horizontal lines
	for yy in range(ymn, ymx):
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xmn, yy, clr)
		setAOV(warpUi, dbName, dbImgDic, lev, nLevels, xmx, yy, clr)
	

def growCurves(warpUi, jtGrid, inSurfGridPrev, frameDir):
	nLevels = warpUi.parmDic("nLevels")
	nCurves = 0
	res = (len(jtGrid), len(jtGrid[0]))
	print "\ngrowing curves for", frameDir
	
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



	# Grow curves following the con(nection)s in jtGrid

	nextPrintout = 10
	print "Progress:"
	for y in range(res[1]):
		pct = int(100*float(y)/res[1])
		if pct >= nextPrintout:
			print "%d%%" % pct # in place didn't update enough: print "Progress %d%%\r" % pct,
			nextPrintout += 10
		for x in range(res[0]):
			#print "x,y", x, y
			for lev in range(nLevels):
				levMult = (lev+1.0)/nLevels
				if inSurfNow[lev]:
					sid = inSurfs[lev][-1].cid
					inSurfNowVal = vX255(clrs[sid%len(clrs)])
					setAOV(warpUi, "inSurfNow", dbImgDic, lev, nLevels, x, y, inSurfNowVal)
					
				val = (0, 0, 0)
				if len(inSurfs[lev]) > 0:
					val = vX255(ut.multVSc(red, len(inSurfs[lev])))
				if len(inHoles[lev]) > 0:
					val = ut.vAdd(val, vX255(ut.multVSc(green, len(inHoles[lev]))))
				if not val == (0, 0, 0):
					val = ut.multVSc(val, .5)
					val = ut.clampVSc(val, 0, 255)
					setAOV(warpUi, "surfsAndHoles", dbImgDic, lev, nLevels, x, y, val)


			# Initiate curve growth for any joints in this cell of jtGrid.

			for lev,jts in jtGrid[x][y].items():
				for jt in jts:
					if jt.cv == None:
						jt.cv = curve(jt, nCurves, inSurfNow[lev])
						nCurves += 1
						xx = x + jt.cons[1][0]
						yy = y + jt.cons[1][1]
						for jtt in jtGrid[xx][yy][lev]:
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
						jt.cv.avgXy = (float(xx)/nJoints, float(xx)/nJoints)
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
			# -- END OF for lev,jts in jtGrid[x][y].items():

			
			# Work out which prev surf the cur surfs are in.

			for lev in range(nLevels):
				levMult = (lev+1.0)/nLevels
				inPrevClr = grey if lev == 0 else None
				if inSurfNow[lev]:
					currentSid = inSurfs[lev][-1].surf.sid
					sidClr = intToClr(currentSid)
					setAOV(warpUi, "sid", dbImgDic, lev, nLevels, x, y, sidClr)
					inPrevClr = green
					inSurfGrid[lev][x][y] = currentSid
					if (inSurfGridPrev == None or
						(not len(inSurfGridPrev) == len(inSurfGrid)) or # TODO: add or if floor(ofs) > floor(preOfs)
						(not math.floor(warpUi.getOfsWLev(lev)) == math.floor(warpUi.getOfsWLev(lev, warpUi.parmDic("fr")-1))) or 
						(not len(inSurfGridPrev[0]) == len(inSurfGrid[0]))) : # NOTE:  this is apparently NOT the same as "if inSurfGridPrev:"
						# There is no prev grid or it is a different res.
						inPrevClr = red
					else:
						# There is a surfGrid file for the previous frame.
						inSurfPrev = inSurfGridPrev[lev][x][y]
						if inSurfPrev == None:
							# There are NO surfs at this level at this cell in the previous frame.
							inPrevClr = red
							if not currentSid in curToPrevSidDic[lev].keys():
								inPrevClr = blue

								# There are no prev sids corresponding to the current sid.
								# If there's nothing in the prev frame here and you haven't
								# recorded anything in curToPrevSidDic, record an empty list.
								# TODO: Do you really need above conditional?  Just repeately re-set it?
								# MAYBE TRY A *SET*!
								curToPrevSidDic[lev][currentSid] = []
						else:
							# There ARE surfs in this cell in the previous frame.
							if currentSid in curToPrevSidDic[lev].keys():
								# There is already a list for currentSid in curToPrevSidDic,
								# append inSurfPrev to that list.

								if not inSurfPrev in curToPrevSidDic[lev][currentSid]:
									curToPrevSidDic[lev][currentSid].append(inSurfPrev)
							else:
								# There's no list for currentSid, make a new one with just inSurfPrev
								curToPrevSidDic[lev][currentSid] = [inSurfPrev]

				if inPrevClr:
					setAOV(warpUi, "inPrev", dbImgDic, lev, nLevels, x, y, vX255(inPrevClr))


	# Draw the curve joint to joint - I think this is just for debug.

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
			headId = cv.head.jid
			jt = cv.head
			sfClr = intToClr(jt.cv.surf.sid)
			while True:
				xx, yy = jt.xy
				setAOV(warpUi, "cvSid", dbImgDic, lev, nLevels, xx, yy, sfClr)
				sfClr = intToClr(jt.cv.cid)
				setAOV(warpUi, "cidPost", dbImgDic, lev, nLevels, xx, yy, sfClr)
				#print "jt", jt, "jt.nx", jt.pv
				jt = jt.pv
				if jt == None:
					break

			# Draw cvBbx
			drawBbx(warpUi, cv.bbx, "cidPost", dbImgDic, lev, nLevels, sfClr)


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

	mergeKeySidToValSid = [{} for i in range(nLevels)]
	births = [[] for i in range(nLevels)] # NOT YET USED
	sidOldToNew = [{} for i in range(nLevels)]
	allPrevs = [[] for i in range(nLevels)]
	for lev in range(nLevels):
		for sidOld,prevs in curToPrevSidDic[lev].items():
			#pOut("\nsidOld", sidOld, "; prevs", prevs)
			#pOut("allPrevs", allPrevs)
			if len(prevs) == 0:
				births[lev].append(sidOld) # NOT YET USED
			else:
				prevs.sort()
				sidNew = prevs[0]
				if sidOld in allPrevs[lev] and sidNew in sidToCvs[lev].keys():
					# Another sid has the same prev, ie. this is a SPLIT.
					sidToCvs[lev][sidNew]["cvs"] += sidToCvs[lev][sidOld]["cvs"][:] # TODO: why [:]?
					sidToCvs[lev][sidNew]["bbx"] = bbxUnion(sidToCvs[lev][sidNew]["bbx"], sidToCvs[lev][sidOld]["bbx"])
					
				allPrevs[lev] += prevs
				if len(prevs) > 1:
					# Register the merge; elements after the first will merge to the first.
					for prev in prevs[1:]:
						mergeKeySidToValSid[lev][prev] = sidNew
						#pOut("\tmergeKeySidToValSid", mergeKeySidToValSid)
				if sidNew in curToPrevSidDic[lev].keys():
					# TODO: Avoid this by assigning new sids based on largest sid
					# in prev frame, ie. keep track of nSurfs accross frames.
					print "\n----------------------------------------------ERROR, sid already exists! sidNew=", sidNew, "curToPrevSidDic[lev][sidNew]:", curToPrevSidDic[lev][sidNew]
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




	# Merge surfaces for marked sids.

	for lev in range(nLevels):
		print "lev:", lev, "sids to be merged:", mergeKeySidToValSid[lev].keys()
		# Merge branches.
		for sid in set(allPrevs[lev] + sidToSurf[lev].keys()):
			if sid in mergeKeySidToValSid[lev].keys():
				# This sid will be merged.
				sidToMergeTo = mergeKeySidToValSid[lev][sid]
				#pOut("Merging sid", sid, "as tid", sidToMergeTo)
				if sidToMergeTo in warpUi.tidToSids[lev].keys():
					warpUi.tidToSids[lev][sidToMergeTo]["sids"].add(sid)
				else:
					warpUi.tidToSids[lev][sidToMergeTo] = {"sids":set([sid])}
				if sid in sidToCvs[lev].keys():
					#cvsToAdd = sidToCvs[lev][sid]["cvs"]
					if sidToMergeTo in sidToCvs[lev].keys():
						sidToCvs[lev][sidToMergeTo]["cvs"] += sidToCvs[lev][sid]["cvs"]
						#sidToCvs[lev][sidNew]["cvs"] += sidToCvs[lev][sidOld]["cvs"]
						sidToCvs[lev][sidToMergeTo]["bbx"] = bbxUnion(sidToCvs[lev][sid]["bbx"], sidToCvs[lev][sidToMergeTo]["bbx"])
					else:
						sidToCvs[lev][sidToMergeTo] = sidToCvs[lev][sid]

				# having merged the sid branch, delete it.
				if sid in warpUi.tidToSids[lev].keys():
					print "\t\tdeleting from tidToSids, sid=", sid
					del(warpUi.tidToSids[lev][sid])
				if sid in sidToCvs[lev].keys():
					print "\t\tdeleting from sidToCvs, sid=", sid
					del(sidToCvs[lev][sid])
			elif not sid in warpUi.sidToTid[lev].keys(): # Make sure this sid isn't already in a tid.
				# This sid will not be merged, it will be a tid.
				pOut("Adding sid", sid, "as tid")
				if sid in warpUi.tidToSids[lev].keys():
					warpUi.tidToSids[lev][sid]["sids"].add(sid)
				else:
					warpUi.tidToSids[lev][sid] = {"sids" : set([sid])}

		# Translate tidToSids to sidToTid. # TODO: Is this really what this does?
		#for tid,sids in warpUi.tidToSids[lev].items():
		for tid,sidData in warpUi.tidToSids[lev].items():
			sids = sidData["sids"]
			#print "\n&&&&& lev:", lev, "tid", tid, "sids", sids, "\n"
			#print "&&&&& tidToSids[lev]:"
			#pprint.pprint(warpUi.tidToSids[lev])
			#print "\n&&&&& sidToCvs[lev]:"
			#pprint.pprint(sidToCvs[lev])
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

	

	# Save db image with new sids.

	for lev in range(nLevels):
		for y in range(res[1]):
			for x in range(res[0]):
				#print "JJJJJ lev", lev, ", sidOld", sidOld
				sidOld = inSurfGrid[lev][x][y]
				if not sidOld == None:
					if lev <= (len(sidOldToNew) + 1) and sidOld in sidOldToNew[lev].keys():
						#print "SETTING lev", lev, ", sidOld", sidOld, ",  sidOldToNew[lev][sidOld]", sidOldToNew[lev][sidOld]
						sidNew = sidOldToNew[lev][sidOld]
						inSurfGrid[lev][x][y] = sidNew
					else:
						sidNew = sidOld
					setAOV(warpUi, "sidPost", dbImgDic, lev, nLevels, x, y, intToClr(sidNew))
		for sid in sidToCvs[lev].keys():
			drawBbx(warpUi, sidToCvs[lev][sid]["bbx"], "sid", dbImgDic, lev, nLevels, intToClr(sid))
		for tid, turfData in warpUi.tidToSids[lev].items():
			#print "\n\ntid", tid
			#print "turfData"
			#pprint.pprint(turfData)
			#print '\n'
			if "bbx" in turfData.keys(): # TODO should bbx always be in turfData.keys()?
				drawBbx(warpUi, turfData["bbx"], "sid", dbImgDic, lev, nLevels, intToClr(tid))
						#sidToCvs[lev][sidToMergeTo]["cvs"] += sidToCvs[lev][sid]["cvs"]


	print "Saving debug images", dbImgDic.keys()
	for debugInfo,imgs in dbImgDic.items():
		for lev in range(nLevels+1):
			levStr = "ALL" if lev == nLevels else "lev%02d" % lev
			levDir,imgPath = warpUi.getDebugDirAndImg(debugInfo, levStr)
			ut.mkDirSafe(levDir)
			pygame.image.save(imgs[lev], imgPath)

	return inSurfGrid, sidToCvs

	#-- END OF growCurves(warpUi, jtGrid, inSurfGridPrev):


def writeTidImg(warpUi, inSurfGrid):
	print "______ in writeTidImg"
	res = (len(inSurfGrid[0]), len(inSurfGrid[0][0]))
	nLevels = warpUi.parmDic("nLevels")
	dbImgDic = {}
	dbImgDic["tid"] = [pygame.Surface(res) for i in range(nLevels+1)][:]
	allTids = set()
	for y in range(res[1]):
		print ("in writeTidImg, y=", y);
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
	#pOut("writeTidImg, allTids", allTidsLs)

	for lev in range(nLevels+1):
		levStr = "ALL" if lev == nLevels else "lev%02d" % lev
		levDir,imgPath = warpUi.getDebugDirAndImg("tid", levStr)
		ut.mkDirSafe(levDir)
		print "imgPath", imgPath
		pygame.image.save(dbImgDic["tid"][lev], imgPath)



def genData(warpUi, statsDirDest):
	ut.timerStart(warpUi, "genData")
	print "\n\n\n"
	print "#####################"
	print "### DOING genData ###"
	print "#####################"

	#os.system("rm " + outFile)
	nLevels = warpUi.parmDic("nLevels")
	img = pygame.image.load(warpUi.images["source"]["path"])
	border(img)

	# Make required dirs.
	fr, frameDir = warpUi.makeFramesDataDir()

	sidToCvs = {}

	if warpUi.parmDic("doRenCv") == 1:
		if warpUi.tidToSids == None:
			pOut("warpUi.tidToSids == None; loading", warpUi.seqDataVDir  + "/tidToSids")
			warpUi.tidToSids = pickleLoad(warpUi.seqDataVDir  + "/tidToSids")
		if warpUi.sidToTid == None:
			pOut("warpUi.sidToTid == None; loading", warpUi.seqDataVDir  + "/sidToTid")
			warpUi.sidToTid = pickleLoad(warpUi.seqDataVDir  + "/sidToTid")
#		pp = pprint.pformat(warpUi.sidToTid)
#		pOut("before renCv warpUi.sidToTid", pp)

		catchErrors = True
		if catchErrors:
			renCvWrapper(warpUi)
			#try:
			#	renCvWrapper(warpUi, warpUi.res)
			#except:
			#	if warpUi.parmDic("anim") == 1:
			#		warpUi.animButCmd()
			#	print "\nERROR: could not perform renCvWrapper; unknown error."
			#	err = sys.exc_info()
			#	warpUi.setStatus("error", ("ERROR:" + str(err)))
			#	print "ERROR:"
			#	print err
		else:
			renCvWrapper(warpUi, warpUi.res)
		print "Post renCvWrapper"
	else:
		# Load prev inSurfGrid.
		inSurfGridPrev = None
		frameDirPrev = warpUi.framesDataDir + ("/%05d" % (fr-1))

		jtGrid, tholds = initJtGrid(img, warpUi)

		inSurfGrid, sidToCvs = growCurves(warpUi, jtGrid, warpUi.inSurfGridPrev, frameDir)
		# TODO: TEMP - this should be done in warp.py when genData is stopped.
		print "\n\n ----- doing pickleDump(" + frameDir + "/inSurfGrid"
		pickleDump(frameDir + "/inSurfGrid", inSurfGrid)

		frameDirLs = frameDir.split("/")
		prevFr = int(frameDirLs[-1]) - 1
		frameDirLs[-1] = "%05d" % prevFr
		prevFrInSurfGrid = "/".join(frameDirLs) + "/inSurfGrid"
		print "\n\n\n prevFrInSurfGrid:", prevFrInSurfGrid, "\n\n"
		if os.path.exists(prevFrInSurfGrid):
			ut.exeCmd("rm " + prevFrInSurfGrid)

		warpUi.inSurfGridPrev = inSurfGrid[:]

	
		# Save inSurfGrid
		#pickleDump(frameDir + "/surfGrid", inSurfGrid)
		#pp = pprint.pformat(sidToCvs)
		#pOut("GEN: sidToCvs", pp)
		#pOut("GEN: sidToCvDic")
		sidToCvDic = convertCvDicToDic(sidToCvs, warpUi)
		#for lev,sidToCv in sidToCvDic.items():
		#	for sid,cvs in sidToCv.items():
		#		pOut("\tsid", sid)
		#		for cv in cvs:
		#			pOut("\t\tlen(cv)", len(cv))
		pickleDump(frameDir + "/sidToCvDic", sidToCvDic)
		pickleDump(frameDir + "/tholds", tholds)
		# Save sidToCvs for this frame.
		pickleDump(warpUi.seqDataVDir + "/tidToSids", warpUi.tidToSids)

		tidToSidsBackupEvery = 20
		if fr % tidToSidsBackupEvery == 0:
			print "BACKING UP tidToSids:"
			ut.exeCmd("cp " + warpUi.seqDataVDir + "/tidToSids " + frameDir)

		pickleDump(warpUi.seqDataVDir + "/sidToTid", warpUi.sidToTid)

	print "Post renCvWrapper block"
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
	print "Doing convertCvDicToDic..."
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

	return ret
	#sidToCvs[lev][sid].append(cv)

def convertCvDicToDicOLD(cvDic, warpUi):
	print "Doing convertCvDicToDicOLD..."
	nLevels = warpUi.parmDic("nLevels")
	ret = {} # Could be list instead of dic
	for lev in range(nLevels):
		surfDic = cvDic[lev]
		ret[lev] = {} # To be filed with surf dics.
		for sid,sidData in surfDic.items():
			cvLs = []
			for cv in sidData["cvs"]:
				cvLs.append(convertCvToLs(cv))
			ret[lev][sid] = cvLs

	return ret
	#sidToCvs[lev][sid].append(cv)

def renCvWrapper(warpUi):
	fr, frameDir = warpUi.makeFramesDataDir()
	sidToCvDic = pickleLoad(frameDir + "/sidToCvDic")
	tholds = pickleLoad(frameDir + "/tholds")
	if sidToCvDic == None:
		if warpUi.parmDic("anim") == 1:
			warpUi.animButCmd()
		warpUi.setStatus("error", "ERROR: sidToCvDic == None")
	else:
		pOut("\nIn renCvWrapper, about to do renCv()...")
		renCv(warpUi, sidToCvDic, tholds)



def calcProg(warpUi, sid, level):
	random.seed(sid)
	progDur = warpUi.parmDic("progDur")
	progStartMin = .2
	progStart = ut.mix(progStartMin, 1-progDur, random.random())
	#progEnd = min(1.0, progStart+warpUi.parmDic("progDur"))
	progEnd = progStart + progDur*2
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
	#print "\n relsPostSmooth:", relsPostSmooth, "rels", rels, "relSizeF", relSizeF, "resF", resF
	
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

def setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, jy, tx, ty, sidRanClr, alpha):
	texClr = srcImg.get_at((jx, jy))
	texClr = list(texClr)[:3]
	cTripMin = .1
	cTripMax = .5
	cTripPow = 1
	mixTrip = ut.mix(cTripMin, cTripMax, pow(prog, cTripPow))
	clr = ut.mixV(texClr, sidRanClr, mixTrip)

	# Adapted from  setAOV(warpUi, "ren", outputs, lev, nLevels, jx + tx, jy + ty, clr)
	thisDic = outputs["ren"]
	prevVal = black
	jxt = jx + tx
	jyt = jy + ty
	if lev <= len(thisDic): # TODO: Won't this always be true?
		res = thisDic[lev].get_size()
		if jxt < res[0] and jxt > -1 and jyt < res[1] and jyt > -1:
			newVal = tuple(list(clr) + [255])
			thisDic[lev].set_at((jxt,jyt), newVal)

			# Comp for ALL level
			prevVal = thisDic[nLevels].get_at((jxt,jyt))
			newVal = ut.mixV(prevVal, newVal, alpha)
			r = warpUi.parmDic("cDark")
			g = warpUi.parmDic("cMid")
			b = warpUi.parmDic("cLight")
			#print "rgb", r, g, b
			#newVal = toClrSpace(r, g, b, newVal)
			newValLs = []
			for v in newVal:
				newValLs.append(int(v))
			newVal = tuple(newValLs)
			newVal = ut.clampVSc(newVal, 0, 255)
			#print "newVal", newVal
			thisDic[nLevels].set_at((jxt,jyt), newVal)



	

def renSid(warpUi, srcImg, sid, nLevels, lev, level, alpha, res, sidToCvDic, outputs, bbx, bbxSize, relSize, thold, falseArray):
	#sidRanClr = ut.multVSc(intToClr(sid), levMult*1.0/nLevels)
	# TODO: Change levMult to levOpac + integrate that.
	sidRanClr = intToClr(sid)


	prog = calcProg(warpUi, sid, level)
	tx,ty = calcXf(warpUi, prog, res, relSize, bbx)
	#tx,ty = (0, 0)

	# TODO: You don't have to include the whole sidToCvDic, just sidToCvDic[lev]
	cvs = sidToCvDic[lev][sid]["cvs"]
	allCoords = []

	# This shouldn't be necessary - inelegant way of removing vertical stripe artifacts
	dirtyPix = list(falseArray)
	#dirtyPix = [[False for y in range(res[1])] for x in range(res[0])] 
	
	for cv in cvs: # TODO: Delete this, and "False" part below
		allCoords += cv

	for cv in cvs:
		iJt = 0
		while iJt < len(cv):
			jt = cv[iJt]
			jtNext = cv[(iJt+1) % len(cv)]
			jtPrev = cv[(iJt-1) % len(cv)]
			jx,jy = list(jt)

			surfAlpha = alpha * (1-prog)
			surfAlpha = min(1.0, 3*surfAlpha)
			#surfAlpha = 1
			curveAlpha = min(1.0, 3*surfAlpha)

			if jx < jtNext[0] or jx > jtPrev[0]:
				# Skip to the top (lowest #) of a vertical line
				while (jtNext[0] == jx	# next x is same - vertical line
						and jtNext[1] < jy):   # next y is lower
					iJt += 1
					jx,jy = list(cv[iJt])
					jtNext = cv[(iJt+1) % len(cv)]
					setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, jy, tx, ty, sidRanClr, curveAlpha)
					dirtyPix[jx][jy] = True
				if jtNext[0] < jx:
					# If the next x is less than this x -- which I think would only happen if
					# the above while loop landed us at a back-curving turn - skip this jt.
					# TODO: must this next line exist?
					setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, jy, tx, ty, sidRanClr, curveAlpha)
					dirtyPix[jx][jy] = True
					iJt += 1
					continue

				#yy = jy +1

				# MAIN FILLING - Draw vertical line up to next curve in this sid.
				yy = jy
				while (int(avgLs(srcImg.get_at((jx,yy))[:-1])) > thold*255) and yy > 0:
					if not dirtyPix[jx][yy]:
						setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, yy, tx, ty, sidRanClr, surfAlpha)
						dirtyPix[jx][yy] = True
					yy -= 1


			# Draw the curve. 
			setRenCvFromTex(warpUi, prog, srcImg, outputs, lev, nLevels, jx, jy, tx, ty, sidRanClr, curveAlpha)

			iJt += 1



def renCv(warpUi, sidToCvDic, tholds):
	
	print "\n\n\n"
	print "*******************"
	print "*** DOING renCv ***"
	print "*******************"

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

	print "\n\ntholds:", tholds
	print "levsSortedByTholds:", levsSortedByTholds

	#for levNotOfs in range(nLevels):
	#	ofs = int(warpUi.getOfs() * nLevels)
	#	lev = int(math.floor(levNotOfs - ofs)) % nLevels
	#	print "\nnLevels:", nLevels, "	levNotOfs:", levNotOfs, "	ofs:", ofs, "	lev:", lev
	#	lev = levNotOfs
	#for lev in levsSortedByTholds[warpUi.parmDic("startLev"):]:

	falseArray = [[False for y in range(res[1])] for x in range(res[0])] 
	for thold, lev in tholdsAndLevLs[warpUi.parmDic("startLev"):]:
		tids = warpUi.tidToSids[lev].keys()
		iTid = 0
		nTids = len(tids)
		print "lev:", lev, "thold:", thold, "nTids:", nTids
		for tid in tids:
			iTid += 1
			print "\r\ttid:", tid, ("(%d of %d)" % (iTid, nTids)), "sids:",
			sids = warpUi.tidToSids[lev][tid]["sids"]

			level = warpUi.getOfsWLev(lev) % 1.0

			# Fade in and out - TODO: Improve this
			alpha = level* (1-level)**2
			alpha = min(level*1.5*pow(thold,.5), 1)

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
						renSid(warpUi, srcImg, sid, nLevels, lev, level, alpha, res, sidToCvDic, outputs, bbx, bbxSize, relSize, thold, falseArray)
		print




	for name in renOutputsMultiLev:
		for lev in range(nLevels+1):
			levStr = "ALL" if lev == nLevels else "lev%02d" % lev
			levDir,imgPath = warpUi.getRenDirAndImg(name, levStr)
			ut.mkDirSafe(levDir)
			print "Saving", name, " image, path:", imgPath
			pygame.image.save(outputs[name][lev], imgPath)
			# TEMP save bmp
			#bmpPath = imgPath.replace(".jpg", ".bmp")
			#pygame.image.save(outputs[name][lev], bmpPath)
			#ut.exeCmd("convert -resize 200% " + bmpPath + " " + bmpPath)

	for name in renOutputsOneLev:
		levDir,imgPath = warpUi.getRenDirAndImg(name)
		ut.mkDirSafe(levDir)
		print "Saving", name, " image, path:", imgPath
		pygame.image.save(outputs[name], imgPath)
		ut.exeCmd("convert -resize 200% " + imgPath + " " + imgPath)

	print "done renCv for fr", warpUi.parmDic("fr")



