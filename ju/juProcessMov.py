#!/usr/bin/python
import sys, os

devDir="/home/jeremy/dev/warp/test/"
sc=.5
sfx=""
lev=""
ext="png"
movFiles = []

if len(sys.argv) == 1:
	print "\nUSAGE: juProcessMov.py [sc=scale] [sfx=sfx] [lev=mn,mx,gam] mov [mov2, mov3..]\n"
	sys.exit()

for arg in sys.argv[1:]:
	if arg[:2] == "sc":
		sc = float(arg.split("=")[1])
	elif arg[:3] == "sfx":
		sfx = arg.split("=")[1]
	elif arg[:3] == "lev":
		lev = arg.split("=")[1]
	elif arg[:3] == "ext":
		ext = arg.split("=")[1]
	else:
		movFiles.append(arg)

print "\nsfx", sfx
print "\nsc", sc
print "\nlev", lev


for movFile in movFiles:
	branch = movFile.split("/")[-1]
	branchWords = branch.split(".")
	branchRoot = ".".join(branchWords[:-1]) + sfx
	tmpStr = ".__TMP__"
	branchRootTmp = branchRoot + tmpStr
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
		sysCmd = ""
		thisBranchRoot = branchRoot if lev == "" else branchRootTmp
		sysCmd += "ffmpeg -i " + movFile + " -vf scale=iw*" + str(sc) + ":ih*" + str(sc) + " -q:v 2 " + seqDir + "/" + thisBranchRoot + ".%05d." + ext

		print "\n###################################"
		print "running:", sysCmd
		print "###################################\n"
		os.system(sysCmd)
		print
		
		if not lev == "":
			imgs = os.listdir(seqDir)
			imgs.sort()
			i = 0
			# Color correct.
			for img in imgs:
				i += 1
				mn,mx,gam = lev.split(",")
				sysCmd = "convert " + seqDir + "/" + img + \
					" -level " + mn + "%," + mx + "%," + gam + " " +\
					seqDir + "/" + img.replace(tmpStr, "") +\
					"; rm " + seqDir + "/" + img
				print i, "of", str(len(imgs)) + "; running:", sysCmd
				os.system(sysCmd)

		# Make textures
		#for img in imgs:
		#	i += 1
		#	sysCmd = "tdlmake " + seqDir + "/" + img + " " + seqDir + "/" + img.replace("img", "tex")
		#	print i, "of", str(len(imgs)) + "; running:", sysCmd
		#	#os.system(sysCmd)


