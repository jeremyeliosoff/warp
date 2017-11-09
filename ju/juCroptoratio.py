#!/usr/bin/python
import os, glob, subprocess, sys

newLeafName = None

if not (len(sys.argv) == 3 or len(sys.argv) == 4):
	print "\nUSAGE: juCroptoratio.py xRatio yRatio [newLeafName]"
	sys.exit()
else:
	xRat = sys.argv[1]
	yRat = sys.argv[2]
	if len(sys.argv) == 4:
		newLeafName = sys.argv[3]

xToY = float(xRat)/float(yRat)


cwd = os.getcwd()
pngPaths = glob.glob(cwd + "/*png")
pngPaths.sort()
info = subprocess.check_output(["identify", pngPaths[0]])
#os.system(sysCmd)
print "info:"
print info

resS = info.split()[2].split("x")
res = (int(resS[0]), int(resS[1]))
print "res",  res

if float(res[0])/res[1] == xToY:
	print "Already same ratio, skipping crop."
else:
	print "Not same ratio: doing crop."
	xNew = int(res[1]*xToY)
	xPad = int(res[0]-xNew)/2
	cmdPrefix = "convert -crop " + str(xNew) + "x" + resS[1] + "+" + str(xPad) + "+0 +repage "


	if newLeafName == None:
		cropDirPath = cwd + "/crop"
	else:
		cropDirPath = cwd + "/" + newLeafName

	#print "making cropDirPath:", cwd
	if not os.path.isdir(cropDirPath):
		print "making cropDirPath:", cropDirPath
		os.makedirs(cropDirPath)
	for pngPath in pngPaths:
		leaf = pngPath.split("/")[-1]
		if not newLeafName == None:
			newLeafAr = leaf.split(".")
			newLeafAr[0] = newLeafName
			leaf = ".".join(newLeafAr)
		cmd = cmdPrefix + " " + pngPath + " " + cropDirPath + "/" + leaf
		print "\tcmd:", cmd
		os.system(cmd)

#2027  convert -crop 810x540+75+0 lzFin2mx40.02222.png test3.png
