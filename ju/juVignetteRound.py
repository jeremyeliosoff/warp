#!/usr/bin/python

##############
# IMPORT
##############
import pygame, os, sys, glob, math

print "sys.argv:", sys.argv

pygame.init()



#img = pygame.Surface(res)

#if len(sys.argv) > 1:
cwd = os.getcwd()
print "cwd:", cwd
#sys.exit()

#rangeDic ={
#"canopy":"100-400",
#}


def dist(a, b):
	dx = a[0] - b[0]
	dy = a[1] - b[1]
	return math.sqrt(dx*dx + dy*dy)


#rng = "1750-2300"
#rng = "1-1245"
rng = "3900-4399" # sub_comingPpl
frStart = 0
fade = 125


seqs = sys.argv[1:]

#seqDic = {
# "newDepMtRDark":{"rng":"1-500", "cent":(.75, .3)},
# "sub_comingPpl":{"rng":"3900-4399", "cent":(.25, .5)},
# #"newArrBUQ_GOODHR":{"rng":"500-1000", "cent":(.22, .48)}, arr
# "newArrBUQ_GOODHR":{"rng":"1000-1500", "cent":(.22, .48)}, # ppl
#}


seqDic = {
 "up_fromBridgeSouthCentered3min":{"rng":"1-500", "cent":(.5, .2), "fade":(150, 150)},
 "sub_comingHR":{"rng":"1650-2325", "cent":(.25, .3), "fade":(300, 250)},
 "newArrBUQ_GOODHR":{"rng":"425-1050", "cent":(.22, .48), "fade":(200, 200)},
 "sub_comingPpl":{"rng":"3800-4400", "cent":(.25, .5), "fade":(250, 150)},
 "newArrBUQ_Ppl":{"rng":"925-1550", "cent":(.22, .48), "fade":(200, 200)}, # ppl
 "sub_going":{"rng":"1750-2300", "cent":(.25, .5), "fade":(200, 200)},
 "newDepMtRDark":{"rng":"1-750", "cent":(.75, .3), "fade":(250, 250)},
 #"newArrBUQ_GOODHR":{"rng":"500-1000", "cent":(.22, .48)}, arr
}

for seq in seqs:
	for seqRoot,vals in seqDic.items():
		if seq[:len(seqRoot)] == seqRoot:
			cent = vals["cent"]
			rng = vals["rng"]
			fade = vals["fade"]
	
	print "seq:", seq
	print "cent:", cent
	print "rng:", rng

#for jpgDir,rng in rangeDic.items():
	if seq[-1] == "/":
		seq = seq[:-1]

	jpgDirPath = cwd + "/" + seq
	print "jpgDirPath", jpgDirPath

	mn,mx = rng.split("-")
	mn = int(mn)
	mx = int(mx)
	print "mn", mn, "mx", mx

	vigDir = jpgDirPath + "_vig"
	if not os.path.isdir(vigDir):
		os.makedirs(vigDir)
	globStr = jpgDirPath + "/*jpg"
	print "globStr:", globStr
	jpgs = glob.glob(globStr)

	globStr = jpgDirPath + "/*png"
	print "globStr:", globStr
	jpgs += glob.glob(globStr)

	jpgs.sort()
	print "jpgs", jpgs
	i = 0
	for jpg in jpgs:
		fr = int(jpg.split(".")[-2])
		if fr < mn or fr > mx or fr < frStart:
			continue
		i += 1
		print "\n### " + str(i) + " of " + str(len(jpgs)) + " ###"
		print "Vignetting " + jpg
		leaf = jpg.split("/")[-1]
		iDot = leaf.index(".")
		leafVig = leaf[:iDot] + "_vig" + leaf[iDot:]
		img = pygame.image.load(jpg)
		res = img.get_size()
		sx,sy = res

		pw = 1
		border = .25

		hsx = border*float(sx)/2
		hsy = border*float(sy)/2
		cxAbs = cent[0] * sx
		cyAbs = cent[1] * sy
		cnrToCent = dist((0,0), (cent[0],cent[1]))
		for x in range(sx):
			for y in range(sy):
				if x < cxAbs:
					xRel = float(x)/(cent[0]*sx) - 1.0
				else:
					xRel = float(x-cxAbs)/(sx-cxAbs)

				if y < cyAbs:
					yRel = float(y)/(cent[1]*sy) - 1.0
				else:
					yRel = float(y-cyAbs)/(sy-cyAbs)

				k = max(0, 1-dist((0,0), (xRel,yRel)))

				# Harden edge
				edgeHard = 2
				inv = 1-k
				for i in range(edgeHard):
					inv *= 1-k
				k = 1-inv
				k *= min(1, (float(fr)-float(mn))/fade[0])
				k *= min(1, (float(mx)-float(fr))/fade[1])

				#if x < hsx:
				#	kx = x/ hsx
				#else:
				#	kx = (sx-x-1)/hsx
				#
				#if y < hsy:
				#	ky = y/ hsy
				#else:
				#	ky = (sy-y-1)/hsy
				#kx = min(1, kx)
				#ky = min(1, ky)
				#
				#k = pow(kx*ky, pw)

				v = img.get_at((x, y))
				#For some reason, the RGB order gets flipped; flip it back.
				img.set_at((x, y), (v[2]*k, v[1]*k, v[0]*k, 1))

		vigPath = vigDir + "/" + leafVig
		print "saving", vigPath
		pygame.image.save(img, vigPath)

		texPath = vigPath.replace(".jpg", ".tex")

