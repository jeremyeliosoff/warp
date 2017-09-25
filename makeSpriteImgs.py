#!/usr/bin/python
import pygame, math, ut, os, pprint, sys, random, time, shutil, glob, genData
from PIL import Image
import numpy as np

#seq = "testPng"
#dataV = "v021"
#frange = range(5,6):
#lrange = range(0,1):
seq = "lzSmokeShortp2pngGm1p3"
dataV = "v063"
#seq = "lzSmokeShortFRpng"
#dataV = "v012GPUNewHope"
frange = range(250,251)
lrange = range(0,10)

def convertTidToClr(tid):
	if tid < 0:
		return (0, 0, 0)
	else:
		if tid == 0: tid = 111111 # Get rid of white, it doesn't tint nicely.
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
			tid = tids[tidPos]
			tidClrGrid[x][y] = convertTidToClr(tidPos)
	
	return tidClrGrid



def vecTo3dArray(v, xres, yres):
	ret = np.repeat([v[:]], yres, 0)
	return np.repeat([ret[:]], xres, 0)

#for fr in range(1,6):
#	for lev in range(4):



def invert255(v):
	return 255-v

invert255V = np.vectorize(invert255)



def makeSpriteDic(srcImg, tidImg, tids, tidPos, tidToSidsThisLev):
	tid = tids[tidPos]
	bbx = tidToSidsThisLev[tid]["bbx"]
	regen = True
	if regen:
		sz=(bbx[1][0]-bbx[0][0], bbx[1][1]-bbx[0][1])

		# +1 totally trial + error. ***********???????? maybe not needed?
		bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
		#print "bbxTup", bbxTup

		# Blit bbx of tid from srcImg to empty cropFromSrcImg of bbx size.
		cropFromSrcImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
		cropFromSrcImg.blit(srcImg, (0, 0), bbxTup)
		#pygame.image.save(cropFromSrcImg, "test/img/%05d_cropFromSrc.png" % tid)

		#pygame.surfarray.pixels_alpha(cropFromSrcImg)[:,:] = 0
		
		# Fill a sprite-sized np array with tidClr based on tidPos.
		tidClr = convertTidToClr(tidPos)
		tidClrAr = vecTo3dArray(tidClr, sz[0], sz[1])

		tidClrBbxImg = pygame.surfarray.make_surface(tidClrAr)
		#pygame.image.save(tidClrBbxImg, "test/img/%05d_idClr.png" % tid)

		# Initialize spriteImg with A=0.
		spriteImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
		pygame.surfarray.pixels_alpha(spriteImg)[:,:] = 0

		# Comp tid using tidClr colorkey - makes hole at tid.
		tidImg.set_colorkey(tidClr)
		spriteImg.blit(tidImg, (0, 0), bbxTup)

		# Invert alpha - TODO: a) quicker (GPU) inversion, ie. OPTIMIZE?
		# b) array_alpha instead because it copies, not references?
		pygame.surfarray.pixels_alpha(spriteImg)[:,:] = \
			invert255V(pygame.surfarray.pixels_alpha(spriteImg)[:,:])
		
		# Copy colours from src.
		pygame.surfarray.pixels3d(spriteImg)[:,:] = \
			pygame.surfarray.pixels3d(cropFromSrcImg)[:,:]

		# Save (tmp?)
		#pygame.image.save(spriteImg, "test/img/%05d_spriteImg.png" % tid)
		spriteImg.fill(tidClr, None, pygame.BLEND_MULT)
	else:
		spriteImg = pygame.image.load("test/img/%05d_spriteImg.png" % tid)
	return {"spriteImg":spriteImg, "bbx":bbx, "tid":tid}


def genSprites(tidPosGrid, tidToSids, srcImg): 
	spritesThisFr = []
	for lev in lrange:
		print "Doing lev", lev, "..."

		tidPosGridThisLev = np.array(tidPosGrid[lev])
		tidToSidsThisLev = tidToSids[lev]

		# Pad to fit img dimensions - no tid for last x or y.
		tidPosGridThisLev = np.lib.pad(tidPosGridThisLev, ((1,0), (0,1)), "constant", constant_values=-1)
		tids = tidToSidsThisLev.keys()
		tids.sort()

		tidClrGrid = converTidPosGridToTidClrGrid(tidPosGridThisLev, tids)
		tidImg = pygame.surfarray.make_surface(tidClrGrid)
		#path = "test/img/tidImg.lev%03d.%05d.png" % (lev, fr)
		#pygame.image.save(tidImg, path)

		spritesThisLev = []

		for tidPos in range(len(tids)):
			spriteDic = makeSpriteDic(srcImg, tidImg, tids, tidPos, tidToSidsThisLev)

			spritesThisLev.append(spriteDic)


		spritesThisFr.append(spritesThisLev)
	return spritesThisFr


def genAndRenSprites():	
	for fr in frange:
		print "Doing fr", fr, "..."
		tidToSidsPath = "/home/jeremy/dev/warp/data/" + seq + "/" + dataV + "/frames/%05d/tidToSids" % fr
		tidToSids = genData.pickleLoad(tidToSidsPath)

		tidPosGridPath = "/home/jeremy/dev/warp/data/" + seq + \
			"/" + dataV + "/frames/%05d/tidPosGrid" % fr
		tidPosGrid = genData.pickleLoad(tidPosGridPath)

		srcPath = "/home/jeremy/dev/warp/seq/" + seq + "/" + seq + ".%05d.png" % fr
		srcImg = pygame.image.load(srcPath)
		res = srcImg.get_size()

		spritesThisFr = genSprites(tidPosGrid, tidToSids, srcImg)
		renSprites(spritesThisFr, res, fr)

		# For debugging.
		pygame.image.save(srcImg, "test/img/_src.%05d.png" % (fr))



def renSprites(spritesThisFr, res, fr):
	print "_renSprites(): BEGIN, fr", fr
	# Initialize canvas
	canvas = pygame.Surface(res, pygame.SRCALPHA, 32)
	canvas.fill((0, 90, 0))
	#for spritesThisLev in spritesThisFr:
	for lev in range(len(spritesThisFr)):
		print "_renSprites(): fr", fr, "lev", lev
		spritesThisLev = spritesThisFr[lev]
		canvasLev = pygame.Surface(res, pygame.SRCALPHA, 32)
		canvasLev.fill((0, 90, 0))
		for spriteDic in spritesThisLev:
			bbx = spriteDic["bbx"]
			bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
			spriteImg = spriteDic["spriteImg"]
			canvas.blit(spriteImg, (bbxTup[0], bbxTup[1]))
			canvasLev.blit(spriteImg, (bbxTup[0], bbxTup[1]))

		pygame.image.save(canvasLev, "test/img/_canvasLev%03d.%05d.png" % (lev,  fr))

	pygame.image.save(canvas, "test/img/_canvas.%05d.png" % (fr))

genAndRenSprites()
