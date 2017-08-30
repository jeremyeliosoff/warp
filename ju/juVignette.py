#!/usr/bin/python

# Dummy change to test commit

##############
# IMPORT
##############
import pygame, os, sys, glob

print "sys.argv:", sys.argv

pygame.init()



#img = pygame.Surface(res)

#if len(sys.argv) > 1:

rangeDic ={
#"angel":"1-300", # 181 min / 299 fr = .61 min/fr
#"balance":"1-101",
"canopy":"100-400",
#"cityMs03":"100-500", # 172 min / 400 fr = .43 min/fr
#"dance24":"110-280", # 59 min / 150 fr = .39 min/fr
#"graves":"200-400",
#"trees":"82-202"
#"lake":"82-282",
#"fbLs04":"200-400",
#"frolick02_10lum":"350-550",
#"hotdog":"75-375",
#"mowJog":"1850-2059",
#"mtnFromConc3":"10-210",
#"sunbeamCu":"244-343",
#"tamFlip":"570-670",
#"tamInCrowd":"200-400",
#"vol":"850-1050"
}

# Total: 412 / 849 = .49 min/fr
# Remaining: 2119 * .49 = 1038 / 60min/hr = 17.3 hr = 6am!

#rangeDic={"vol":"850-1050"}
#rangeDic={"tamInCrowd":"200-400"}

#for jpgDir in sys.argv[1:]:
for jpgDir,rng in rangeDic.items():
	if jpgDir[-1] == "/":
		jpgDir = jpgDir[:-1]
	#if not jpgDir[0] in ["/","~"]:
	#	jpgDir = os.getcwd() + "/" + jpgDir

	jpgDirPath = "/home/jeremy/curves/seq/" + jpgDir
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
	jpgs.sort()
	i = 0
	for jpg in jpgs:
		fr = int(jpg.split(".")[-2])
		if fr < mn or fr > mx:
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
		for x in range(sx):
			for y in range(sy):
					k = float(x)/sx * float(y)/sy
					if x < hsx:
						kx = x/ hsx
					else:
						kx = (sx-x-1)/hsx
					
					if y < hsy:
						ky = y/ hsy
					else:
						ky = (sy-y-1)/hsy
					kx = min(1, kx)
					ky = min(1, ky)
					
					k = pow(kx*ky, pw)

					v = img.get_at((x, y))
					#For some reason, the RGB order gets flipped; flip it back.
					img.set_at((x, y), (v[2]*k, v[1]*k, v[0]*k, 1))

		vigPath = vigDir + "/" + leafVig
		pygame.image.save(img, vigPath)

		texPath = vigPath.replace(".jpg", ".tex")
		cmd = "tdlmake " + vigPath + " " + texPath
		print "Exectuing:", cmd
		os.system(cmd)

