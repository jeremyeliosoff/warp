#!/usr/bin/python
import pygame, math, ut, pickle, os

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


clrs = [red, green, blue, yellow, cyan, magenta, white, rYellow, gYellow, gCyan, bCyan, rMagenta, bMagenta, grey, lRed, lGreen, lBlue, lYellow, lCyan, lMagenta]

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
	prevCids = {}

	def add(self, jt):
		jt.pv = self.head
		if self.head:
			self.head.nx = jt
		self.head = jt
		self.level = jt.level

	def __init__(self, jt, nCurves, inSurf):
		self.inSurf = inSurf
		self.tail = jt
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
	inSurf = None
	inHoles = []
	sid = None
	tid = None

	def __init__(self, inSurf, sid):
		self.inSurf = inSurf
		self.sid = sid
		self.tid = sid



# FUNCTIONS

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


def makeLevelGrid(img, nLevels):
    res = img.get_size()
    levelGrid = [[None for x in range(res[1])] for y in range(res[0])] 
    for x in range(res[0]):
    	for y in range(res[1]):
            clr = img.get_at((x,y))
            intens = avgLs(clr[:-1])/255.0
            levelGrid[x][y] = int(intens * (nLevels+1))/(nLevels) #256 not 255 to cuz white pixels waffled bw 254-255
            #print "lev", levelGrid[x][y]
            #print
    #print "levelGrid",levelGrid
    return levelGrid


def gridToImgV(grid):
    res = (len(grid), len(grid[0]))
    ret = pygame.Surface(res)
    for x in range(res[0]):
        for y in range(res[1]):
            v = ut.vMult(grid[x][y], 255)
            v = ut.clamp(v, 0, 255)
            ret.set_at((x, y), (v[0], v[1], v[2], 255))
    return ret

def gridToImgS(grid):
    res = (len(grid), len(grid[0]))
    ret = pygame.Surface(res)
    for x in range(res[0]):
        for y in range(res[1]):
            v = int(grid[x][y]*255)
            v = int(max(0, min(255, v)))
            ret.set_at((x, y), (v, v, v, 255))
    return ret

def heatMap(v, parmDic):
    cDark = parmDic("cDark")
    cMid = parmDic("cMid")
    cLight = parmDic("cLight")
    if v < .5:
        return ut.mix(cDark, cMid, v/.5)
    else:
        return ut.mix(cMid, cLight, (v-.5)/.5)

def vecToClr(v):
    ret = []
    for i in v:
        ret.append(int(ut.clamp(int(i*255), 0, 255)))
    ret += [255]
    return tuple(ret)





def initJtGrid(img, warpUi):
    ofs = warpUi.parmDic("ofs")
    nLevels = warpUi.parmDic("nLevels")
    kSurf = warpUi.parmDic("kSurf")
    res = img.get_size()
    nJoints = 0
    jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
    gridOut = [[(0, 0, 0) for y in range(res[1]-1)] for x in range(res[0]-1)] 
    levelImg = pygame.Surface(res)
    levThreshs = {}
    usedLevelsInit = []
    for x in range(res[0]-1):
        for y in range(res[1]-1):
            # get current level
            intens = float(avgLs(img.get_at((x,y))[:-1]))/255
            thisLev = math.ceil(nLevels*(-ofs/nLevels + intens))
            vFlt = float(thisLev+ofs)/nLevels
            v = int(255*vFlt)
            v = ut.clamp(v, 0, 255)
            hm = heatMap(vFlt, warpUi.parmDic)
            gridOut[x][y] = ut.vMult(hm, kSurf)
            levelImg.set_at((x, y), (v, v, v, 255))
            # get neighbours.
            nbrs = []
            for yy in range(y, y+2):
                for xx in range(x, x+2):
                    nbrs.append(int(avgLs(img.get_at((xx,yy))[:-1])))

            for lev in range(nLevels):
                levWOfs = float(lev + ofs)
                levThresh = int((levWOfs/nLevels)*255)
                levThreshs[lev] = levThresh
                isHigher = []
                tot = 0
                for nbr in nbrs:
                    higher = 1 if nbr > levThresh else 0
                    tot += higher
                    isHigher.append(higher)
                # Only add joint if different.
                if tot > 0 and tot < 4:
                    if not lev in usedLevelsInit:
                        usedLevelsInit.append(lev)
                    cons = neighboursToConns[tuple(isHigher)]
                    texClr = img.get_at((x,y))
                    if len(cons) > 1:
                        jtGrid[x][y][lev] =  [joint((x,y), levWOfs, texClr, cons[0], nJoints, nbrs),
                                               joint((x,y), levWOfs, texClr, cons[1], nJoints + 1, nbrs),]
                        nJoints += 2
                    else:
                        jtGrid[x][y][lev] = [joint((x,y), levWOfs, texClr, cons[0], nJoints, nbrs)]
                        nJoints += 1

    
    #warpUi.gridJt = jtGrid[:]
    warpUi.gridOut = gridOut[:]
    print ">>>>>>>>>>>>>> saving", warpUi.images["ren"]["path"]
    renPath = warpUi.images["ren"]["path"]
    renSeqDir = "/".join(renPath.split("/")[:-1])
    ut.mkDirSafe(renSeqDir)
    print "||||||||||| saving", renPath
    pygame.image.save(gridToImgV(warpUi.gridOut),  renPath)


    print "==============="
    print "==============="
    print "==============="
    print "==============="
    print "levThreshs", levThreshs
    print "usedLevelsInit", usedLevelsInit
    print "==============="
    return jtGrid
    
def growCurves(warpUi, jtGrid, inSurfGridPrev):
    # Old growCurves() return values that are seemingly not needed:
    # inCurvesGrid, surfDics
    # Maybe just for debugging:
    # curves, allCurves, inOutImg, inSurfImgs, 

    # The pickles written AND READ (only surfGrid is in genData):
    # /surfGrid, /surfDics, /surfCurToPrevSidDic, /surfSidToTid"
    nLevels = warpUi.parmDic("nLevels")
    #jointMax = warpUi.parmDic("jointMax")
    nCurves = 0
    nSurfs = 0
    totJoints = 0
    res = (len(jtGrid), len(jtGrid[0]))
    print "///////// res", res


    # inHoles delimit holes; inSurfs do not.
    curToPrevSidDic = [{}] * nLevels
    surfs = [[]] * nLevels
    inHoles = [[]] * nLevels
    inSurfs = [[]] * nLevels
    inSurfNow = [False] * nLevels
    curves = [[]] * nLevels

    inSurfGrid = [[[None for yy in range(res[1])] for xx in range(res[0])] for lev in range(nLevels)]

    contCondition = True
    imgJtInOut = pygame.Surface(res)
    dbImgs = ["inSurfNow", "surfsAndHoles", "inPrev"]
    dbImgDic = {}
    for dbi in dbImgs:
        # The last cell - that is, [nLevels] - is reserved for "all"
        dbImgDic[dbi] = [pygame.Surface(res) for i in range(nLevels+1)][:]


    allIndeces = []
    for y in range(res[1]):
        for x in range(res[0]):
            #print "x,y", x, y
            for lev in range(nLevels):
                levMult = (lev+1.0)/nLevels
                if inSurfNow[lev]:
                    index = inSurfs[lev][-1].cid
                    if not index in allIndeces:
                        allIndeces.append(index)
                    #print ">>>>>>>>>>>>>>>>> index", index
                    inSurfNowVal = vX255(clrs[index%len(clrs)])
                    dbImgDic["inSurfNow"][lev].set_at((x, y), inSurfNowVal)
                    dbImgDic["inSurfNow"][nLevels].set_at((x, y), ut.vMult(inSurfNowVal, levMult))
                    
                val = (0, 0, 0)
                if len(inSurfs[lev]) > 0:
                    val = vX255(ut.vMult(red, len(inSurfs[lev])))
                if len(inHoles[lev]) > 0:
                    val = ut.vAdd(val, vX255(ut.vMult(green, len(inHoles[lev]))))
                if not val == (0, 0, 0):
                    val = ut.vMult(val, .5)
                    val = ut.clamp(val, 0, 255)
                    #print "xxxxxx val", val
                    dbImgDic["surfsAndHoles"][lev].set_at((x,y), val)
                    dbImgDic["surfsAndHoles"][nLevels].set_at((x,y), ut.vMult(val, levMult))

            for lev,jts in jtGrid[x][y].items():
                for jt in jts:
                    if jt.cv == None:
                        #print "\t growing curve " + str(nCurves) + "..."
                        jt.cv = curve(jt, nCurves, inSurfNow[lev])
                        nCurves += 1
                        xx = x + jt.cons[1][0]
                        yy = y + jt.cons[1][1]
                        for jtt in jtGrid[xx][yy][lev]:
                            if jtt.cons[0][0] == -jt.cons[1][0] and jtt.cons[0][1] == -jt.cons[1][1]:
                                thisJt = jtt
                        nJoints = 0
                        while thisJt.cv == None and contCondition:
                            totJoints += 1
                            nJoints += 1
                            thisJt.cv = jt.cv
                            jt.cv.add(thisJt)
                            xx += thisJt.cons[1][0]
                            yy += thisJt.cons[1][1]

                            for jtt in jtGrid[xx][yy][lev]:
                                if jtt.cons[0][0] == -thisJt.cons[1][0] and  jtt.cons[0][1] == -thisJt.cons[1][1]:
                                    thisJt = jtt
                            #contCondition = totJoints < jointMax
                        curves[lev] = curves[lev][:] + [jt.cv]

#                        if not contCondition:
#                            break
#                    if not contCondition:
#                        break
#                if not contCondition:
#                    break
#            if not contCondition:
#                break
                    # Register when entering or leaving a curve.  By convention, only look at y = -1 direction.
                    if jt.cons[0][1] == -1 or jt.cons[1][1] == -1:
                        if jt.cons[0][1] == -1:
                            imgJtInOut.set_at((x, y), (255, 0, 0))
                        else:
                            imgJtInOut.set_at((x, y), (0, 255, 0))
                        imgJtInOut.set_at((x, y), vX255(clrs[jt.cv.cid%len(clrs)]))

                        inSurfNow[lev] = not inSurfNow[lev]
                        # It APPEARS that inSurfs[] and inHoles[] keep track of which
                        # hole and non-hole curves you are in now (at x,y), respectively.
                        # NOTE: these are arrays because you can be inside multiple 
                        # surfs and mutiple holes at once.
                        if inSurfNow[lev]:
                            #Case 1: closing outSurf
                            if len(inHoles[lev]) > 0 and inHoles[lev][-1] == jt.cv:
                                inHoles[lev].pop()
                            #Case 2: this is a new inSurf
                            else:
                                if jt.cv.surf == None:
                                    thisSurf = surf(jt.cv, nSurfs)
                                    surfs[lev] = surfs[lev][:] + [thisSurf]
                                    jt.cv.surf = thisSurf

                                    thisSurfDic = {"inSurf": jt.cv, "sid": nSurfs, "inHoles": []}
                                    jt.cv.surfDic = thisSurfDic
                                    nSurfs += 1
                                if not jt.cv in inSurfs[lev]:
                                    inSurfs[lev] = inSurfs[lev][:] + [jt.cv]
                        else:
                            #Case 3: closing inSurf
                            if len(inSurfs[lev]) > 0 and inSurfs[lev][-1] == jt.cv:
                                inSurfs[lev] = inSurfs[lev][:-1]
                            #Case 3: this is a new outSurf
                            else:
                                #if not jt.cv in inSurfs[lev][-1].surf.inHoles:
                                if not jt.cv in inSurfs[lev][-1].surfDic["inHoles"]:
                                    inSurfs[lev][-1].surf.inHoles = inSurfs[lev][-1].surf.inHoles[:] + [jt.cv]
                                    inSurfs[lev][-1].surfDic["inHoles"] = inSurfs[lev][-1].surfDic["inHoles"][:] + [jt.cv]
                                inHoles[lev] = inHoles[lev][:] + [jt.cv]

                        #print "^^^^^^^^^^^^^^^ lev", lev, " inHoles[lev]", inHoles[lev], "inSurfs[lev]", inSurfs[lev], "inSurfNow[lev]", inSurfNow[lev]
#
#
#
            # -- END OF for lev,jts in jtGrid[x][y].items():

            for lev in range(nLevels):
                levMult = (lev+1.0)/nLevels
                #print "inSurfNow[" + str(lev) + "]", inSurfNow[lev]
                inPrevClr = grey if lev == 0 else None
                if inSurfNow[lev]:
                    #print "---------------------- eeeeeeeeeee"
                    inPrevClr = green
                    currentSid = inSurfs[lev][-1].surf.sid
                    inSurfGrid[lev][x][y] = currentSid
                    if inSurfGridPrev == None or (not len(inSurfGridPrev) == len(inSurfGrid)) or (not len(inSurfGridPrev[0]) == len(inSurfGrid[0])) : # NOTE:  this is apparently NOT the same as "if inSurfGridPrev:"
                        inPrevClr = red
                    else:
                        # There is a surfGrid file for the previous frame.
                        inSurfPrev = inSurfGridPrev[lev][x][y]
                        if inSurfPrev == None:
                            # There are NO surfs at this level at this cell in the previous frame.
                            inPrevClr = red
                            if not currentSid in curToPrevSidDic[lev].keys():
                                inPrevClr = blue

                                # Looks like some acrobatics here to get around reference/referred issues...
                                # TODO: At least TRY to make it less fugly.
                                # Anyway, the idea is, if there's nothing in the prev frame here and you
                                # haven't recorded anything in curToPrevSidDic, record an empty list.
                                # TODO: Do you really need above conditional?  Just repeately re-set it?
                                newLs = curToPrevSidDic[:]
                                newDic = newLs[lev].copy()
                                newDic[currentSid] = []
                                newLs[lev] = newDic.copy()
                                curToPrevSidDic = newLs[:]
                        else:
                            # There ARE surfs in this cell in the previous frame.
                            if currentSid in curToPrevSidDic[lev].keys():
                                # There is already a list for currentSid in curToPrevSidDic,
                                # append inSurfPrev to that list.

                                if not inSurfPrev in curToPrevSidDic[lev][currentSid]:
                                    #curToPrevSidDic[lev][currentSid].append(inSurfPrev)
                                    #curToPrevSidDic[lev][currentSid] = curToPrevSidDic[lev][currentSid][:] + [inSurfPrev]
                                    newLs = curToPrevSidDic[:]
                                    newDic = newLs[lev].copy()
                                    newDic[currentSid] = newDic[currentSid][:] + [inSurfPrev]
                                    newLs[lev] = newDic.copy()
                                    curToPrevSidDic = newLs[:]
                            else:
                                # There's no list for currentSid, make a new one with just inSurfPrev
                                newLs = curToPrevSidDic[:]
                                newDic = newLs[lev].copy()
                                newDic[currentSid] = [inSurfPrev]
                                newLs[lev] = newDic.copy()

                if inPrevClr:
                    dbImgDic["inPrev"][lev].set_at((x,y), vX255(inPrevClr))
                    dbImgDic["inPrev"][nLevels].set_at((x,y), ut.vMult(vX255(inPrevClr), levMult))
            # -- END OF for lev in range(nLevels):
            #dbImgDic["inPrev"][lev].set_at((x,y), green)

    
    #print "\n\nallIndeces:", allIndeces

    # Draw the curve joint to joint - I think this is basically just for debug.
    drawCurveGrid = [[[0, 0, 0] for y in range(res[1])] for x in range(res[0])] 
    curveId = 0
    for lev in range(nLevels):
        for cv in curves[lev]:
            headId = cv.head.jid
            jt = cv.head
            while True:
                xx, yy = jt.xy
                drawCurveGrid[xx][yy] = clrs[cv.cid % len(clrs)]
                #print "jt", jt, "jt.nx", jt.pv
                jt = jt.pv
                if jt == None:
                    break


    drawCurveImg = gridToImgV(drawCurveGrid)
    #pygame.image.save(drawCurveImg, warpUi.images["curves"]["path"])
    fr = warpUi.parmDic("fr")
    for debugInfo,imgs in dbImgDic.items():
        for lev in range(nLevels+1):
            # Debug images are organized like so (ALL CAPS or numbers means placeholder):
            # ../dev/warp/data/SEQNAME/v00/debugImg/DATAINFO/lev00/fr.00000.jpg
            levStr = "ALL" if lev == nLevels else "lev%02d" % lev
            levDir,imgPath = warpUi.getDebugDirAndImg(debugInfo, levStr)
            ut.mkDirSafe(levDir)
            #print "============== warpUi.seqDataDir:", warpUi.seqDataDir, " -- saving", imgPath
            print "|||||||||||-- saving debug img", imgPath
            pygame.image.save(imgs[lev], imgPath)
    return inSurfGrid

    #-- END OF growCurves(warpUi, jtGrid, inSurfGridPrev):


def genData(warpUi):
    print "\n\n\n"
    print "#####################"
    print "### DOING genData ###"
    print "#####################"
    nLevels = warpUi.parmDic("nLevels")
    ofs = warpUi.parmDic("ofs")
    img = pygame.image.load(warpUi.images["source"]["path"])
    border(img)

    # Make required dirs.
    frameDir = warpUi.makeFramesDataDir()

    # Load prev inSurfGrid.
    inSurfGridPrev = None
    fr = warpUi.parmDic("fr")
    frameDirPrev = warpUi.framesDataDir + ("/%05d" % (fr-1))
    if os.path.exists(frameDirPrev):
        inSurfGridPrevFile = open(frameDirPrev + "/surfGrid", 'r')
        inSurfGridPrev = pickle.load(inSurfGridPrevFile)
        inSurfGridPrevFile.close()
    


    jtGrid = initJtGrid(img, warpUi)
    inSurfGrid = growCurves(warpUi, jtGrid, inSurfGridPrev)

    # Save inSurfGrid
    inSurfGridFile = open(frameDir + "/surfGrid", 'w')
    pickle.dump(inSurfGrid, inSurfGridFile)
    inSurfGridFile.close()

