#!/usr/bin/python
import os, glob, subprocess, sys

cwd = os.getcwd()
pngPaths = glob.glob(cwd + "/*png")
pngPaths.sort()
info = subprocess.check_output(["identify", pngPaths[0]])
#os.system(sysCmd)
print "info:"
print info


resS = info.split()[2].split("x")
res = (int(resS[0]), int(resS[1]))
newRes = (res[0]-1, res[1]-1)
print "res",  res

thisSubdir = cwd.split("/")[-1]
print "thisSubdir:", thisSubdir

if thisSubdir == "retime":
	cmdPrefix = "convert -crop " + newRes[0] + "x" + newRes[1] + "+0+0 +repage "
else:
	cmdPrefix = "convert -crop " + newRes[0] + "x" + newRes[1] + "+1+1 +repage "

cropDirPath = parentDir + "/crop"

if not os.path.isdir(cropDirPath):
	print "making cropDirPath:", cropDirPath
	os.makedirs(cropDirPath)

for pngPath in pngPaths:
	leaf = pngPath.split("/")[-1]
	cmd = cmdPrefix + " " + pngPath + " " + cropDirPath + "/" + leaf
	print "\tcmd:", cmd
	os.system(cmd)
