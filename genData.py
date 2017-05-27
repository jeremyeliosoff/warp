#!/usr/bin/python
import pygame, math, ut, pickle, os, pprint, sys

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
red,     # 0
green,   # 1
blue,    # 2
yellow,  # 3
cyan,    # 4
magenta, # 5
white,   # 6
rYellow, # 7
gYellow, # 8
gCyan,   # 9
bCyan,   # 10
rMagenta,# 11
bMagenta,# 12
grey,    # 13
lRed,    # 14
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

def pickleDump(filePath, data):
    print "Pickle dumping", filePath, "..."
    with open(filePath, 'w') as dataFile:
        pickle.dump(data, dataFile)

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
    print "In initJtGrid..."
    ofs = warpUi.parmDic("ofs")
    nLevels = warpUi.parmDic("nLevels")
    kSurf = warpUi.parmDic("kSurf")
    res = img.get_size()
    nJoints = 0
    jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
    gridOut = [[(0, 0, 0) for y in range(res[1]-1)] for x in range(res[0]-1)] 
    levelImg = pygame.Surface(res)
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
                isHigher = []
                tot = 0
                for nbr in nbrs:
                    higher = 1 if nbr > levThresh else 0
                    tot += higher
                    isHigher.append(higher)
                # Only add joint if different.
                if tot > 0 and tot < 4:
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
    renPath = warpUi.images["ren"]["path"]
    renSeqDir = "/".join(renPath.split("/")[:-1])
    ut.mkDirSafe(renSeqDir)
    print "SAVING RENDERED IMAGE:", renPath
    # TODO: maybe use a more general purpose version of setDbIMg instead.
    pygame.image.save(gridToImgV(warpUi.gridOut),  renPath)


    return jtGrid

def setDbIMg(name, dbImgDic, lev, nLevels, x, y, val, db=False):
    levMult = (lev+1.0)/nLevels
    if db:
        print "setting", name, ", lev:", lev, "x,y", x,y
    dbImgDic[name][lev].set_at((x,y), val)
    dbImgDic[name][nLevels].set_at((x,y), ut.vMult(val, levMult))

def intToClr(i):
    return vX255(clrs[i%len(clrs)])
    
def growCurves(warpUi, jtGrid, inSurfGridPrev, frameDir):
    nLevels = warpUi.parmDic("nLevels")
    nCurves = 0
    res = (len(jtGrid), len(jtGrid[0]))
    print "\ngrowing curves for", frameDir


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
    dbImgs = ["inSurfNow", "surfsAndHoles", "inPrev", "cid", "cvSid", "cidPost", "sid", "sidPost", "sidPre", "tid"]
    dbImgDic = {}
    for dbi in dbImgs:
        # The last cell - that is, [nLevels] - is reserved for "all"
        dbImgDic[dbi] = [pygame.Surface(res) for i in range(nLevels+1)][:]


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
                    setDbIMg("inSurfNow", dbImgDic, lev, nLevels, x, y, inSurfNowVal)
                    
                val = (0, 0, 0)
                if len(inSurfs[lev]) > 0:
                    val = vX255(ut.vMult(red, len(inSurfs[lev])))
                if len(inHoles[lev]) > 0:
                    val = ut.vAdd(val, vX255(ut.vMult(green, len(inHoles[lev]))))
                if not val == (0, 0, 0):
                    val = ut.vMult(val, .5)
                    val = ut.clamp(val, 0, 255)
                    setDbIMg("surfsAndHoles", dbImgDic, lev, nLevels, x, y, val)

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
                        
                        # Grow the actual curve.
                        cvClr = intToClr(jt.cv.cid)
                        while thisJt.cv == None:
                            nJoints += 1
                            setDbIMg("cid", dbImgDic, lev, nLevels, xx, yy, cvClr)
                            thisJt.cv = jt.cv
                            jt.cv.add(thisJt)
                            xx += thisJt.cons[1][0]
                            yy += thisJt.cons[1][1]

                            for jtt in jtGrid[xx][yy][lev]:
                                if jtt.cons[0][0] == -thisJt.cons[1][0] and  jtt.cons[0][1] == -thisJt.cons[1][1]:
                                    thisJt = jtt
                        jt.cv.nJoints = nJoints
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

            for lev in range(nLevels):
                levMult = (lev+1.0)/nLevels
                inPrevClr = grey if lev == 0 else None
                if inSurfNow[lev]:
                    currentSid = inSurfs[lev][-1].surf.sid
                    sidClr = intToClr(currentSid)
                    setDbIMg("sid", dbImgDic, lev, nLevels, x, y, sidClr)
                    inPrevClr = green
                    inSurfGrid[lev][x][y] = currentSid
                    if inSurfGridPrev == None or (not len(inSurfGridPrev) == len(inSurfGrid)) or (not len(inSurfGridPrev[0]) == len(inSurfGrid[0])) : # NOTE:  this is apparently NOT the same as "if inSurfGridPrev:"
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
                    setDbIMg("inPrev", dbImgDic, lev, nLevels, x, y, vX255(inPrevClr))
            # -- END OF for lev in range(nLevels):
            #dbImgDic["inPrev"][lev].set_at((x,y), green)

    
    #print "\n\nallIndeces:", allIndeces

    #print "\n\n|||||| CIDs ||||||"
    #for lev in range(nLevels):
    #    print "--lev", lev
    #    for cv in curves[lev]:
    #        print "sid", cv.surf.sid, ", cid", cv.cid

    # Draw the curve joint to joint - I think this is basically just for debug.
    drawCurveGrid = [[[0, 0, 0] for y in range(res[1])] for x in range(res[0])] 
    curveId = 0
    sidToCvs = [{} for i in range(nLevels)]
    sidToSurf = [{} for i in range(nLevels)]
    cidToCurve = [{} for i in range(nLevels)]
    for lev in range(nLevels):
        #print "YYYXXX lev", lev, "sidToCvs[lev].keys():", sidToCvs[lev].keys()
        for cv in curves[lev]:
            cidToCurve[lev][cv.cid] = cv
            sid = cv.surf.sid
            if sid in sidToCvs[lev].keys():
                # THERE MUST BE A BETTER WAY!!
                sidToCvs[lev][sid].append(cv)
            else:
                sidToCvs[lev][sid] = [cv]
            #print "XXX lev", lev, ", sid", sid, "sidToCvs[lev].keys():", sidToCvs[lev].keys()
            
            sidToSurf[lev][sid] = cv.surf
            headId = cv.head.jid
            jt = cv.head
            while True:
                xx, yy = jt.xy
                sfClr = intToClr(jt.cv.surf.sid)
                setDbIMg("cvSid", dbImgDic, lev, nLevels, xx, yy, sfClr)
                sfClr = intToClr(jt.cv.cid)
                setDbIMg("cidPost", dbImgDic, lev, nLevels, xx, yy, sfClr)
                drawCurveGrid[xx][yy] = clrs[cv.cid % len(clrs)]
                #print "jt", jt, "jt.nx", jt.pv
                jt = jt.pv
                if jt == None:
                    break


    #print "---------curToPrevSidDic"
    #pprint.pprint(curToPrevSidDic)

    mergeKeyToVal = [{} for i in range(nLevels)]
    births = [[] for i in range(nLevels)]
    sidOldToNew = [{} for i in range(nLevels)]
    #allPrevs = [set() for i in range(nLevels)]
    allPrevs = [[] for i in range(nLevels)]
    for lev in range(nLevels):
        #print "%%% lev", lev
        #print "sidToCvs[lev].keys()       :",sidToCvs[lev].keys()
        #print "sidToSurf[lev].keys()      :",sidToSurf[lev].keys()
        #print "curToPrevSidDic[lev].keys():",curToPrevSidDic[lev].keys()
        for sidOld,prevs in curToPrevSidDic[lev].items():
            if len(prevs) == 0:
                births[lev].append(sidOld)
                
            else:
                prevs.sort()
                #allPrevs[lev].union(set(prevs))
                allPrevs[lev] += prevs
                sidNew = prevs[0]
                if len(prevs) > 1:
                    # Register the merge; elements after the first will merge to the first.
                    for prev in prevs[1:]:
                        mergeKeyToVal[lev][prev] = sidNew
                if sidNew in curToPrevSidDic[lev].keys():
                    # TODO: Avoid this by assigning new sids based on largest sid
                    # in prev frame, ie. keep track of nSurfs accross frames.
                    print "\n----------------------------------------------ERROR, sid already exists! sidNew=", sidNew, "curToPrevSidDic[lev][sidNew]:", curToPrevSidDic[lev][sidNew]
                    continue
                if not sidNew == sidOld:
                    sidToCvs[lev][sidNew] = sidToCvs[lev][sidOld]
                    del(sidToCvs[lev][sidOld])
                    sidToSurf[lev][sidNew] = sidToSurf[lev][sidOld]
                    del(sidToSurf[lev][sidOld])
                    sidOldToNew[lev][sidOld] = sidNew


    for lev in range(nLevels*0):
        print "\n--------------------lev", lev
        #sidDicThisLev = sidToCurves[lev]
        sidDicThisLev = sidToCvs[lev]
        for sid,cvSet in sidDicThisLev.items():
            print "\n---sid:", sid
            thisSurf =  sidToSurf[lev][sid]
            print "\t inSurf.cid", thisSurf.inSurf.cid, ", nJoints:", thisSurf.inSurf.nJoints
            print "\t inHoles",
            for ih in thisSurf.inHoles:
                print "cid:", ih.cid, ", nJoints:", ih.nJoints, "|",
            print
            print "\t sid", thisSurf.sid
            print "\t tid", thisSurf.tid
            #prevSid = curToPrevSidDic[lev][thisSurf.sid]
            #print "\t prevSid", prevSid



            for cv in cvSet:
                print "----- cv.cid", cv.cid



    for lev in range(nLevels):
        print "lev:", lev, "sids to be merged:", mergeKeyToVal[lev].keys()
        # Merge branches.
        for sid in set(allPrevs[lev] + sidToSurf[lev].keys()):
            #print "--sid", sid, "lev", lev, "warpUi", warpUi, "warpUi.sidToTid", warpUi.sidToTid
            if sid in mergeKeyToVal[lev].keys():
                # This sid will be merged.
                mergeTo = mergeKeyToVal[lev][sid]
                if mergeTo in warpUi.tidToSids[lev].keys():
                    warpUi.tidToSids[lev][mergeTo].add(sid)
                else:
                    warpUi.tidToSids[lev][mergeTo] = set([sid])

                # having merged the sid branch, delete it.
                if sid in warpUi.tidToSids[lev].keys():
                    print "deleting from tidToSids, sid=", sid
                    del(warpUi.tidToSids[lev][sid])
            elif not sid in warpUi.sidToTid[lev].keys(): # Make sure this sid isn't already in a tid.
                # This sid will not be merged, it will be a tid.
                if sid in warpUi.tidToSids[lev].keys():
                    warpUi.tidToSids[lev][sid].add(sid)
                else:
                    warpUi.tidToSids[lev][sid] = set([sid])

        # Translate tidToSids to sidToTid.
        for tid,sids in warpUi.tidToSids[lev].items():
            for sid in sids:
                warpUi.sidToTid[lev][sid] = tid
    

    # Save db image with new sids.
    for y in range(res[1]):
        for x in range(res[0]):
            for lev in range(nLevels):
                #print "JJJJJ lev", lev, ", sidOld", sidOld
                sidOld = inSurfGrid[lev][x][y]
                if not sidOld == None:
                    setDbIMg("sidPre", dbImgDic, lev, nLevels, x, y, intToClr(sidOld))
                    #print "YYYYYYYes sidOld", sidOld
                    if lev <= (len(sidOldToNew) + 1) and sidOld in sidOldToNew[lev].keys():
                        #print "SETTING lev", lev, ", sidOld", sidOld, ",  sidOldToNew[lev][sidOld]", sidOldToNew[lev][sidOld]
                        sidNew = sidOldToNew[lev][sidOld]
                        inSurfGrid[lev][x][y] = sidNew
                    else:
                        sidNew = sidOld
                    setDbIMg("sidPost", dbImgDic, lev, nLevels, x, y, intToClr(sidNew))


    fr = warpUi.parmDic("fr")
    print "Saving debug images", dbImgDic.keys()
    for debugInfo,imgs in dbImgDic.items():
        for lev in range(nLevels+1):
            # Debug images are organized like so (ALL CAPS or numbers means placeholder):
            # ../dev/warp/data/SEQNAME/v00/debugImg/DATAINFO/lev00/fr.00000.jpg
            levStr = "ALL" if lev == nLevels else "lev%02d" % lev
            levDir,imgPath = warpUi.getDebugDirAndImg(debugInfo, levStr)
            ut.mkDirSafe(levDir)
            pygame.image.save(imgs[lev], imgPath)


#def saveCurToPrevSidDic(frameDir, curToPrevSidDic):
    td = open(frameDir + "/curToPrevSidDic.txt", 'w')
    for lev in range(len(curToPrevSidDic)):
        td.write("\n\n--------------\nlev: " + str(lev))
        curToPrevSidDicThisLev = curToPrevSidDic[lev]
        for sidCur,sidPrevs in curToPrevSidDicThisLev.items():
            td.write("\n\nsidCur: " + str(sidCur) + "\nsidPrev: ")
            for sidPrev in sidPrevs:
                td.write("\t" + str(sidPrev))
    td.close()
            
    pickleDump(frameDir + "/surfCurToPrevSidDic", curToPrevSidDic)

    return inSurfGrid, sidToCvs

    #-- END OF growCurves(warpUi, jtGrid, inSurfGridPrev):


def writeTidImg(warpUi, inSurfGrid):
    print "______ in writeTidImg"
    res = (len(inSurfGrid[0]), len(inSurfGrid[0][0]))
    nLevels = warpUi.parmDic("nLevels")
    dbImgDic = {}
    dbImgDic["tid"] = [pygame.Surface(res) for i in range(nLevels+1)][:]
    for y in range(res[1]):
        for x in range(res[0]):
            for lev in range(nLevels):
                sid = inSurfGrid[lev][x][y]
                #print "sid is", sid,
                if not sid == None:
                    #print ".%%%%%%% lev", lev, "sid", sid
                    if sid in warpUi.sidToTid[lev].keys():
                        tid = warpUi.sidToTid[lev][sid]
                        #print ".%%%%%%% tid", tid
                        setDbIMg("tid", dbImgDic, lev, nLevels, x, y, intToClr(tid))

    for lev in range(nLevels+1):
        levStr = "ALL" if lev == nLevels else "lev%02d" % lev
        levDir,imgPath = warpUi.getDebugDirAndImg("tid", levStr)
        ut.mkDirSafe(levDir)
        print "imgPath", imgPath
        pygame.image.save(dbImgDic["tid"][lev], imgPath)

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
    fr, frameDir = warpUi.makeFramesDataDir()

    sidToCvs = {}

    if warpUi.parmDic("justRenTid") == 1:
        inSurfGrid = pickleLoad(frameDir + "/surfGrid")
        warpUi.tidToSids = pickleLoad(warpUi.seqDataDir  + "/tidToSids")
        warpUi.sidToTid = pickleLoad(warpUi.seqDataDir  + "/sidToTid")
        writeTidImg(warpUi, inSurfGrid)
    else:
        # Load prev inSurfGrid.
        inSurfGridPrev = None
        frameDirPrev = warpUi.framesDataDir + ("/%05d" % (fr-1))
        inSurfGridPrev = pickleLoad(frameDirPrev + "/surfGrid")

        jtGrid = initJtGrid(img, warpUi)
        inSurfGrid, sidToCvs = growCurves(warpUi, jtGrid, inSurfGridPrev, frameDir)

    
        # Save inSurfGrid
        inSurfGridFile = open(frameDir + "/surfGrid", 'w')
        pickleDump(frameDir + "/surfGrid", inSurfGrid)



    
    # Save tidToSids and sidToTid for whole seq.
    pickleDump(warpUi.seqDataDir + "/tidToSids", warpUi.tidToSids)
    pickleDump(warpUi.seqDataDir + "/sidToTid", warpUi.sidToTid)
    # Save sidToCvs for this frame.
    pickleDump(frameDir + "/sidToCvs", sidToCvs)

