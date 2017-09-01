#!/usr/bin/python
import sys, os

devDir="/home/jeremy/dev/warp/test/"
sc=.5
sfx=""
movFiles = []

if len(sys.argv) == 1:
	print "\nUSAGE: juProcessMov.py [sc=scale] [sfx=sfx] mov [mov2, mov3..]\n"
	sys.exit()

for arg in sys.argv[1:]:
	if arg[:2] == "sc":
		sc = float(arg.split("=")[1])
	elif arg[:3] == "sfx":
		sfx = arg.split("=")[1]
	else:
		movFiles.append(arg)

print "\nsfx", sfx
print "\nsc", sc


for movFile in movFiles:
	branch = movFile.split("/")[-1]
	branchWords = branch.split(".")
	branchRoot = ".".join(branchWords[:-1]) + sfx
	suffix = branchWords[-1]
	seqDir = devDir + "seq/" + branchRoot
	print
	print "branch", branch
	print "branchRoot", branchRoot
	print "seqDir", seqDir
	if os.path.isdir(seqDir):
		print "\n" + seqDir + " already exists!!!"
	else:
		os.makedirs(seqDir)
		#sysCmd = "ffmpeg -i " + movFile + " -r 60 -vf scale=iw*" + str(sc) + ":ih*" + str(sc) + " -q:v 2 " + seqDir + "/" + branchRoot + ".%04d.jpg"
		sysCmd = "ffmpeg -i " + movFile + " -vf scale=iw*" + str(sc) + ":ih*" + str(sc) + " -q:v 2 " + seqDir + "/" + branchRoot + ".%05d.jpg"
		print "\n###################################"
		print "running:", sysCmd
		print "###################################\n"
		os.system(sysCmd)
		print
		jpgs = os.listdir(seqDir)
		jpgs.sort()
		i = 0
		# Make textures
		#for jpg in jpgs:
		#	i += 1
		#	sysCmd = "tdlmake " + seqDir + "/" + jpg + " " + seqDir + "/" + jpg.replace("jpg", "tex")
		#	print i, "of", str(len(jpgs)) + "; running:", sysCmd
		#	#os.system(sysCmd)


