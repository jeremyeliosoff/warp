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

def invert255(v):
	return 255-v

invert255V = np.vectorize(invert255)


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
			sz=(bbx[1][0]-bbx[0][0], bbx[1][1]-bbx[0][1])

			# +1 totally trial + error.
			bbxTup = (bbx[0][0]+1, bbx[0][1]+1, bbx[1][0], bbx[1][1])
			print "bbxTup", bbxTup

			# Blit bbx of tid from srcImg to empty cropFromSrcImg of bbx size.
			cropFromSrcImg = pygame.Surface(sz, pygame.SRCALPHA, 32)
			cropFromSrcImg.blit(srcImg, (0, 0), bbxTup)
			pygame.image.save(cropFromSrcImg, "test/img/%05d_cropFromSrc.png" % tid)

			pygame.surfarray.pixels_alpha(cropFromSrcImg)[:,:] = 0
			sprites.append({"img":cropFromSrcImg, "bbx":bbx, "tid":tid})
			
			# Fill a sprite-sized np array with tidClr based on tidPos.
			tidClr = convertTidToClr(tidPos)
			tidClrAr = vecTo3dArray(tidClr, sz[0], sz[1])

			tidClrBbxImg = pygame.surfarray.make_surface(tidClrAr)
			pygame.image.save(tidClrBbxImg, "test/img/%05dTidClr.png" % tid)

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
			pygame.surfarray.pixels3d(spriteImg)[:,:] = \
				pygame.surfarray.pixels3d(cropFromSrcImg)[:,:]
			pygame.image.save(spriteImg, "test/img/%05dBgImgCB_CkeyInvAlphaOrigClr.png" % tid)

