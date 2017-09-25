#!/usr/bin/python
import pygame, math, ut, os, pprint, sys, random, time, shutil, glob, genData
from PIL import Image
import numpy as np

tidToSidsPath = base = "/home/jeremy/dev/warp/data/testPng/v021/frames/%05d/tidToSids" % 5

def convertTidToClr(tid):
	if tid < 0:
		return (0, 0, 0)
	else:
		octant = tid%8
		tDiv = tid/8
		ocR = tDiv % 128 + 128*(octant % 2)
		tDiv = tDiv/128
		ocG = tDiv % 128 + 128*(octant/2 % 2)
		tDiv = tDiv/128
		ocB = tDiv % 128 + 128*(octant/4 % 2)# This should never loop - till we get to tid = 256^3
		return (255-ocR, 255-ocG, 255-ocB)

#def converTidPosGridToClrGrid(tidPosGrid, tids):
#	xres = len(tidPosGrid)
#	yres = len(tidPosGrid[0])
#	tidPosClrGrid = np.zeros((xres, yres) + (3,), dtype=np.uint8)
#	
#	for x in range(xres):
#		for y in range(yres): 
#			tidPos = tidPosGrid[x][y]
#			tidPosClrGrid[x][y] = convertTidToClr(tidPos)
#	
#	return tidPosClrGrid

def converTidPosGridToTidClrGrid(tidPosGrid, tids):
	xres = len(tidPosGrid)
	yres = len(tidPosGrid[0])
	tidClrGrid = np.zeros((xres, yres) + (3,), dtype=np.uint8)
	
	for x in range(xres):
		for y in range(yres): 
			tidPos = tidPosGrid[x][y]
			tid = tids[tidPos]
			tidClrGrid[x][y] = convertTidToClr(tidPos)
	
	return tidClrGrid


def vecTo3dArray(v, xres, yres):
	ret = np.repeat([v[:]], yres, 0)
	return np.repeat([ret[:]], xres, 0)

#for fr in range(1,6):
#	for lev in range(4):


for fr in range(5,6):
	for lev in range(0,1):
		srcPath = "/home/jeremy/dev/warp/seq/testPng/testPng.%05d.png" % fr

		base = "/home/jeremy/dev/warp/data/testPng/v021/frames/%05d" % fr
		tidPosGridPath = base + "/tidPosGrid"

		tidPosGrid = genData.pickleLoad(tidPosGridPath)
		tidPosGridThisLev = tidPosGrid[lev]

		tidToSids = genData.pickleLoad(tidToSidsPath)
		tidToSidsThisLev = tidToSids[lev]
		tids = tidToSidsThisLev.keys()
		tids.sort()

		tidClrGrid = converTidPosGridToTidClrGrid(tidPosGridThisLev, tids)
		tidGridSz = (len(tidClrGrid), len(tidClrGrid[0]))
		#tidImg = pygame.Surface(tidGridSz)
		#pygame.pixelcopy.array_to_surface(tidImg, tidClrGrid)
		tidImg = pygame.surfarray.make_surface(tidClrGrid)
		path = "test/img/tidImg.lev%03d.%05d.png" % (lev, fr)
		pygame.image.save(tidImg, path)

		print "tids", tids
		srcImg = pygame.image.load(srcPath)
		sprites = []

		for tidPos in range(len(tids)):
			tid = tids[tidPos]
			bbx = tidToSidsThisLev[tid]["bbx"]
			#print "\ntid", tid
			#print "bbx", bbx
			sz=(bbx[1][0]-bbx[0][0], bbx[1][1]-bbx[0][1])
			destImg = pygame.Surface(sz, pygame.SRCALPHA, 32)


			# +1 totally trial + error.
			bbxTp = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
			print "bbxTp", bbxTp

			# Blit bbx of tid from srcImg to empty destImg of bbx size.
			destImg.blit(srcImg, (0, 0), bbxTp)
			path = "test/img/%05d.png" % tid
			pygame.image.save(destImg, path)

			pygame.surfarray.pixels_alpha(destImg)[:,:] = 0
			sprites.append({"img":destImg, "bbx":bbx, "tid":tid})

			tidClr = convertTidToClr(tidPos)
			print "\n\nXXX tidClr", tidClr

			tidClrOfs = ((tidClr[0] + 128) % 256, tidClr[1], tidClr[2])
			#bgAr.fill([255, 0, 0])
			print "bgAr = np.empty(sz) - sz = ", sz
			tidClrAr = vecTo3dArray(tidClr, sz[0], sz[1])
			tidClrOfsAr = vecTo3dArray(tidClrOfs, sz[0], sz[1])
			#bgImg = Image.fromarray(bgAr, 'RGB')

			tidClrOfsBbxImg = pygame.surfarray.make_surface(tidClrOfsAr)
			pygame.image.save(tidClrOfsBbxImg, "test/img/%05dTidClrOfsBbxImg.png" % tid)
			tidClrBbxImg = pygame.surfarray.make_surface(tidClrAr)
			pygame.image.save(tidClrBbxImg, "test/img/%05dTidClr.png" % tid)

			#bgAr.fill(200)
			bgAr = np.empty(sz)
			bgImg = pygame.surfarray.make_surface(bgAr)
			pygame.image.save(bgImg, "test/img/%05dBgImgA_Org.png" % tid)

			tidImg.set_colorkey((0, 0, 10))
			bgImg = pygame.surfarray.make_surface(bgAr)
			bgImg.blit(tidImg, (0, 0), bbxTp)
			pygame.image.save(bgImg, "test/img/%05dBgImgB_NoCkey.png" % tid)

			tidImg.set_colorkey(tidClr)
			bgImg = pygame.surfarray.make_surface(bgAr)
			bgImg.blit(tidImg, (0, 0), bbxTp)
			pygame.image.save(bgImg, "test/img/%05dBgImgC_Ckey.png" % tid)

			#destImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
			bgImg = pygame.surfarray.make_surface(bgAr)
			# LAST CHANGE vvvv
			bgImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
			pygame.surfarray.pixels_alpha(bgImg)[:,:] = 0
			bgImg.blit(tidClrOfsBbxImg, (0, 0), bbxTp)
			pygame.image.save(bgImg, "test/img/%05dBgImgD_CkeyTidClr.png" % tid)







			#x = sz[0]/2
			#y = sz[1]/2
			#print "get at", x, y, destImg.get_at((0, 0))
			#print destImgAr

		res = srcImg.get_size()

		for x in range(res[0]-1):
			for y in range(res[1]-1):
				tidPos = tidPosGridThisLev[x][y]
				if tidPos > -1:
					bbx = sprites[tidPos]["bbx"]
					xs = x-bbx[0][0]+0
					ys = y-bbx[0][1]-1
					#print "tidPos", tidPos, "tid", tids[tidPos], "bbx", bbx, "xy", x, y, "xys", xs, ys,
					#print "shape", pygame.surfarray.array3d(sprites[tidPos]["img"]).shape
					sptImg = sprites[tidPos]["img"]
					sz = sptImg.get_size()
					if xs >= 0 and ys >= 0 and xs < sz[0] and ys < sz[1]:
						pygame.surfarray.pixels_alpha(sptImg)[xs][ys] = 255

		for sprite in sprites:
			path = "test/img/tid%05d.lev%03d.%05d.png" % (sprite["tid"], lev, fr)
			#pygame.image.save(sprite["img"], path)

