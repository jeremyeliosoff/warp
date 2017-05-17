#!/usr/bin/python
import pygame, math, utils

GlevGamma = 1

outImgs = []

clrs = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 0],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
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

def makeLevelGrid(img, nLevels):
    res = img.get_size()
    levelGrid = [[None for x in range(res[1])] for y in range(res[0])] 
    for x in range(res[0]):
    	for y in range(res[1]):
            clr = img.get_at((x,y))
            #print "clr", clr
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
            v = utils.vMult(grid[x][y], 255)
            v = utils.clamp(v, 0, 255)
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
        #return utils.mix((.2, .2, 1), (1, 0, 0), v/.5)
        return utils.mix(cDark, cMid, v/.5)
    else:
        #return utils.mix((1, 0, 0), (0, 1, 0), (v-.5)/.5)
        return utils.mix(cMid, cLight, (v-.5)/.5)

def vecToClr(v):
    ret = []
    for i in v:
        ret.append(int(utils.clamp(int(i*255), 0, 255)))
    ret += [255]
    return tuple(ret)


def jtGridToImg(grid, parmDic):
    nLevels = parmDic("nLevels")
    res = (len(grid), len(grid[0]))
    ret = pygame.Surface(res)
    usedLevels = []
    for x in range(res[0]):
        for y in range(res[1]):
            v = 0
            vec = [0, 0, 0]

            for k in grid[x][y].keys():
                thisVal = float(k)/(nLevels-1)
                hm = heatMap(thisVal, parmDic)
                vec = utils.vAdd(vec, hm)
                if not k in usedLevels:
                    usedLevels.append(k)
                #print "<<<<<<<<<<<<<<<< k", k, ", thisVal", thisVal, "hm", hm, ", vec", vec
            
            #print ">>>>>>>>>>>> v", v
            #ret.set_at((x, y), (v, v, v, 255))
            #print "-----vec", vec
            ret.set_at((x, y), vecToClr(vec))
    print "usedLevels", usedLevels
    return ret



def initJtGrid(img, parmDic, images):
    ofs = parmDic("ofs")
    nLevels = parmDic("nLevels")
    res = img.get_size()
    nJoints = 0
    jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
    levelImg = pygame.Surface(res)
    levThreshs = {}
    usedLevelsInit = []
    for x in range(res[0]-1):
        for y in range(res[1]-1):
            # get current level
            intens = float(avgLs(img.get_at((x,y))[:-1]))/255
            thisLev = math.ceil(nLevels*(-ofs/nLevels + intens))
            v = int(255*float(thisLev+ofs)/nLevels)
            v = utils.clamp(v, 0, 255)
            levelImg.set_at((x, y), (v, v, v, 255))
            # get neighbours.
            nbrs = []
            for yy in range(y, y+2):
                for xx in range(x, x+2):
                    nbrs.append(int(avgLs(img.get_at((xx,yy))[:-1])))

            for lev in range(nLevels):
                levThresh = int((float(lev + ofs)/nLevels)*255)
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
                        jtGrid[x][y][lev] =  [joint((x,y), lev, texClr, cons[0], nJoints, nbrs),
                                               joint((x,y), lev, texClr, cons[1], nJoints + 1, nbrs),]
                        nJoints += 2
                    else:
                        jtGrid[x][y][lev] = [joint((x,y), lev, texClr, cons[0], nJoints, nbrs)]
                        nJoints += 1

    
    pygame.image.save(jtGridToImg(jtGrid, parmDic), images["jtGrid"]["path"])
    pygame.image.save(levelImg, images["levels"]["path"])
    with open("out", 'w') as f:
        f.write(str(jtGrid))


    print "==============="
    print "==============="
    print "==============="
    print "==============="
    print "levThreshs", levThreshs
    print "usedLevelsInit", usedLevelsInit
    print "==============="
    #print "jtGrid"
    #print jtGrid
    return jtGrid
    
def growCurves(parmDic, images, jtGrid):
    nLevels = parmDic("nLevels")
    animIter = parmDic("animIter")
    nCurves = 0
    nSurfs = 0
    totJoints = 0
    res = (len(jtGrid), len(jtGrid[0]))
    inSurfNow = [False] * nLevels
    curves = [[]] * nLevels
    contCondition = True
    for y in range(res[1]):
        for x in range(res[0]):
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
                            #contCondition = totJoints < animIter

                        curves[lev] = curves[lev][:] + [jt.cv]
                        if not contCondition:
                            break
                    if not contCondition:
                        break
                if not contCondition:
                    break
            if not contCondition:
                break

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
    pygame.image.save(drawCurveImg, images["curves"]["path"])


def saveLevelImg(parmDic, images):
    nLevels = parmDic("nLevels")
    ofs = parmDic("ofs")

    print "yessir"
    img = pygame.image.load(images["orig"]["path"])
    border(img)

    jtGrid = initJtGrid(img, parmDic, images)  #TODO just use parmDic
    growCurves(parmDic, images, jtGrid)
