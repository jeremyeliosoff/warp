#!/usr/bin/python
import pygame, math, utils
imgPath = "/home/jeremy/dev/warp/img/single/testAndP.jpg"
imgPathOut = "/home/jeremy/dev/warp/img/single/levelImg.jpg"
img = pygame.image.load(imgPath)

GnLevels = 3
GlevGamma = 1

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
            #intens = intens ** (1.0/GlevGamma)
            #intens *= 255
            #levelGrid[x][y] = (intens * (1+nLevels)/256)/nLevels #256 not 255 to cuz white pixels waffled bw 254-255
            #levelGrid[x][y] = (nLevels*intens * 255)/nLevels #256 not 255 to cuz white pixels waffled bw 254-255
            levelGrid[x][y] = math.floor(intens * nLevels)/(nLevels-1) #256 not 255 to cuz white pixels waffled bw 254-255
            #print "lev", levelGrid[x][y]
            #print
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

def saveLevelImg(nLevels):
    print "yessir"
    levelGrid = makeLevelGrid(img, nLevels)
    pygame.image.save(gridToImg(levelGrid, 0), imgPathOut)
    return imgPath, imgPathOut
