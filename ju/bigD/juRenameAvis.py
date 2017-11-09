#!/usr/bin/python

import os, sys, glob

fullDir = "/home/jeremy/curves/ren/FULL"
fullDirs = glob.glob(fullDir + "/*")

for dr in fullDirs:
	print "dr:", dr
	avi = dr + "/full.avi"
	print "avi:", avi
	aviGlob = glob.glob(avi)
	if len(aviGlob) > 0:
		leafDr = dr.split("/")[-1]
		dest = avi.replace("full.avi", "full_" + leafDr + ".avi")
		cmd = "mv " + avi + " " + dest
		print "cmd:", cmd
		#os.system(cmd)
	else:
		print "FUUUUUUUUUUCK!"
	print
