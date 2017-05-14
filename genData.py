#!/usr/bin/python
import pygame, math, utils

GlevGamma = 1

outImgs = []

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
            levelGrid[x][y] = math.floor(intens * (nLevels+1))/(nLevels) #256 not 255 to cuz white pixels waffled bw 254-255
            #print "lev", levelGrid[x][y]
            #print
    #print "levelGrid",levelGrid
    return levelGrid


def gridToImg(grid, nLevels):
    res = (len(grid), len(grid[0]))
    ret = pygame.Surface(res)
    for x in range(res[0]):
        for y in range(res[1]):
            v = math.floor(grid[x][y]*255)
            v = int(max(0, min(255, v)))
            ret.set_at((x, y), (v, v, v, 255))
    return ret

def heatMap(v):
    if v < .5:
        return utils.mix((0, 0, 1), (1, 0, 0), v/.5)
    else:
        return utils.mix((1, 0, 0), (1, 1, 0), (v-.5)/.5)

def vecToClr(v):
    ret = []
    for i in v:
        ret.append(int(utils.clamp(math.floor(i*255), 0, 255)))
    ret += [255]
    return tuple(ret)


def jtGridToImg(grid, nLevels):
    res = (len(grid), len(grid[0]))
    ret = pygame.Surface(res)
    for x in range(res[0]):
        for y in range(res[1]):
            v = 0
            vec = [0, 0, 0]

            if not grid[x][y] == {}:
                print
            for k in grid[x][y].keys():
                thisVal = float(k)/(nLevels-1)
                hm = heatMap(thisVal)
                vec = utils.vAdd(vec, hm)
                print "<<<<<<<<<<<<<<<< k", k, ", thisVal", thisVal, "hm", hm, ", vec", vec
            
            #print ">>>>>>>>>>>> v", v
            #ret.set_at((x, y), (v, v, v, 255))
            #print "-----vec", vec
            ret.set_at((x, y), vecToClr(vec))
    return ret



def initJtGrid(levelGrid, img, nLevels):
    res = (len(levelGrid), len(levelGrid[0]))
    nJoints = 0
    jtGrid = [[{} for y in range(res[1]-1)] for x in range(res[0]-1)] 
    for x in range(res[0]-1):
        for y in range(res[1]-1):
            # get neighbours.
            nbrs = []
            for yy in range(y, y+2):
                for xx in range(x, x+2):
                    nbrs.append(levelGrid[xx][yy])

            for lev in range(nLevels):
                #print "XXXXXXXXXXXXXXXXXXXXxx lev", lev, ", levelGrid[" + str(x) + "][" + str(y) + "]: ", levelGrid[x][y]
                isHigher = []
                tot = 0
                for nbr in nbrs:
                    higher = 1 if nbr >= float(lev+1)/(nLevels+1) else 0
                    tot += higher
                    isHigher.append(higher)
                # Only add joint if different.
                if tot > 0 and tot < 4:
                    #print "YYYYYYY nLevels", nLevels, ", lev", lev, ", tot:", tot
                    cons = neighboursToConns[tuple(isHigher)]
                    texClr = img.get_at((x,y))
                    if len(cons) > 1:
                        jtGrid[x][y][lev] =  [joint((x,y), lev, texClr, cons[0], nJoints, nbrs),
                                               joint((x,y), lev, texClr, cons[1], nJoints + 1, nbrs),]
                        nJoints += 2
                    else:
                        jtGrid[x][y][lev] = [joint((x,y), lev, texClr, cons[0], nJoints, nbrs)]
                        nJoints += 1


    pygame.image.save(jtGridToImg(jtGrid, nLevels), utils.imgJtGrid)
    with open("out", 'w') as f:
        f.write(str(jtGrid))

    print "==============="
    print "==============="
    print "==============="
    print "==============="
    print "==============="
    #print "jtGrid"
    #print jtGrid
    return jtGrid
    


def genCurves(levelGrid, img, outImgs, imgPathThisFr, nLevels):
    fr = 0
    ofs = .2
    jtGrid = initJtGrid(levelGrid, img, nLevels)



def saveLevelImg(nLevels):
    print "yessir"
    img = pygame.image.load(utils.imgPath)
    border(img)
    levelGrid = makeLevelGrid(img, nLevels)
    pygame.image.save(gridToImg(levelGrid, 0), utils.imgPathOut)

    genCurves(levelGrid, img, outImgs, utils.imgPath, nLevels)
    return utils.imgPath, utils.imgPathOut
