#!/usr/bin/python
import os, sys, glob
seqDirs = sys.argv[1:-1]
lum = sys.argv[-1]

for seqDir in seqDirs:
	print "seqDir", seqDir, "lum", lum

	imgLs = glob.glob(seqDir + "/*tiff")
	imgLs += glob.glob(seqDir + "/*jpg")
	imgLs.sort()
	suffix = "_" + str(lum) + "lum"
	newDir = seqDir + suffix
	cmdMkdir ="mkdir " + newDir 
	print cmdMkdir
	os.system(cmdMkdir)

	i = 0
	for img in imgLs:
		i +=1 
		leaf = img.split("/")[-1]
		leafLs = leaf.split(".")
		leafLs[0] = leafLs[0] + suffix
		leaf = ".".join(leafLs)
		cmd = "convert -brightness-contrast " + lum + " " + img + " " + newDir + "/" + leaf
		print i, "of", len(imgLs), ":", cmd
		os.system(cmd)
		leafLs[-1] = "tex"
		leafTex = ".".join(leafLs)
		print cmd
		cmd = "tdlmake " + newDir + "/" + leaf + " " + newDir + "/" + leafTex
		os.system(cmd)
