#!/usr/bin/python
import os, sys, glob
seqDirs = sys.argv[1:-1]
crop = sys.argv[-1]


for seqDir in seqDirs:
	print "seqDir", seqDir, "crop", crop

	imgLs = glob.glob(seqDir + "/*jpg")
	imgLs.sort()

	for img in imgLs:
		leaf = img.split("/")[-1]
		cmd = "convert -crop " + crop + " " + img + " " + img
		print cmd
		os.system(cmd)
		leafLs = leaf.split(".")
		leafLs[-1] = "tex"
		leafTex = ".".join(leafLs)
		cmd = "tdlmake " + img + " " + seqDir + "/" + leafTex
		print cmd
		os.system(cmd)
