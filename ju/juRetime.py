#!/usr/bin/python
import sys, os, glob, math

def mix(a, b, m):
	return a * (1.0-m) + b * m

def fit(v, omn, omx, nmn, nmx):
	prog = (v-omn)/(omx-omn)
	return nmn + prog * (nmx-nmn)

def clamp(v, mn, mx):
	return min(mx, max(mn, v))

def smoothstep(edge0in, edge1in, xin):
	edge1 = float(edge1in)
	edge0 = float(edge0in)
	x = float(xin)
	# Scale, bias and saturate x to 0..1 range
	ret = edge1
	if edge1 > edge0:
		x = clamp((x - edge0)/(edge1 - edge0), 0.0, 1.0); 
		# Evaluate polynomial
		ret = x*x*(3 - 2*x);
	return ret


#pngPaths = glob.glob(cwd + "/*png")
#pngPaths.sort()
#for pngPath in pngPaths:

fpsGrps = (
(1, 10, 30), 
(1840, 2090, 25), 
(2270, 2510, 20), 
(2700, 2940, 15), 
(3080, 3350, 10))


frOut = 0

frange = 50

frStart = 1600
frEnd = 3400
#frStart = 3300 # TEMP
#frEnd = 3370 # TEMP
fpsStart = 30
fpsEnd = 5

#for i in range(frange):


if len(sys.argv) > 4:
	print "\nUSAGE: juRetime.py [basename [basenameOut]]\n"
	sys.exit()



baseInOut = []

makeMov=True
addSound=True

for arg in sys.argv[1:]:
	if "=" in arg:
		k,v = arg.split("=")
		if k == "makeMov":
			if v == "False":
				makeMov=False
			continue
		if k == "addSound":
			if v == "addSound":
				addSound=False
			continue
	else:
		baseInOut.append(arg)

cwd = os.getcwd()
cwdSplit = cwd.split("/")

seq = cwdSplit[6]
ver = cwdSplit[7]


baseIn = "ren.ALL"
baseOut = seq + "_" + ver

if len(baseInOut) > 0:
	baseIn = baseInOut[0]
if len(baseInOut) == 2:
	baseOut = baseInOut[1]


formatIn = baseIn + ".%05d.png"
formatOut = baseOut + ".%05d.png"
#while frSrc < frange:
frSrc = frStart
#while frSrc < frEnd:
#	prog = float(frSrc)/(frange-1)
#	incr = mix(1, float(fpsEnd)/fpsStart, prog)
#
#	i = 0
#	for fpsGrp in fpsGrps:
#		#print "fpsGrp[0]", fpsGrp[0]
#		if i >= (len(fpsGrps)-1) or fpsGrps[i+1][0] > frSrc:
#			break
#		i += 1
#	prog = smoothstep(fpsGrp[0], fpsGrp[1], frSrc)
#	fpsPrev = fpsStart if i == 0 else fpsGrps[i-1][2]
#	fpsNext = fpsGrp[2]
#	#print "fpsPrev", fpsPrev, "fpsNext", fpsNext, "prog", prog
#	fps = mix(fpsPrev, fpsNext, prog)
#	incr = float(fps)/fpsStart
#
#	frSrc += incr
#	frA, mixB = divmod(frSrc, 1)
#	frB = frA + 1
#	mixB = frSrc % 1
#	mixA = 1.0 - mixB
#	imgA = formatIn % frA
#	imgB = formatIn % frB
#
#	while (not os.path.exists(imgA)) and frA <= frEnd:
#		print "\t!!!!", imgA, "does not exist! checking next frame..."
#		frA += 1
#		imgA = formatIn % frA
#
#	while (not os.path.exists(imgB)) and frB <= frEnd:
#		print "\t!!!!", imgB, "does not exist! checking next frame..."
#		frB += 1
#		imgB = formatIn % frB
#
#	if not os.path.exists("retime"):
#		os.makedirs("retime")
#
#	imgOut = "retime/" +  formatOut % frOut
#	cmd = "composite -dissolve " + str(int(100*mixA)) + "x" + \
#		str(int(100*mixB)) + " " + imgA + " " + imgB + " " + imgOut
#	print "frOut", frOut, "frSrc", frSrc, ":", cmd
#	#print "frOut", frOut, "i", i, "fpsPrev", fpsPrev, "fpsNext", fpsNext, "fps", fps, "incr", incr, "frSrc", frSrc
#	os.system(cmd)
#	frOut += 1

if makeMov:

	retimeDirPath = cwd + "/retime"
	aviNoSoundPath = retimeDirPath + "/" + baseOut + ".avi"
	print "baseOut:", baseOut
	cmd = "ffmpeg -framerate 30 -i " + retimeDirPath + "/" + baseOut \
		+ ".%05d.png -vcodec libx264 -b 5000k " + aviNoSoundPath
	print "\nExecuting:", cmd, "...\n\n"
	os.system(cmd)

	if addSound:
		#ardUberDir = "/home/jeremy/dev/warp/audio/ardour"
		#ardDirs = glob.glob(ardUberDir + "/*")
		#ardDirs.sort(key=os.path.getmtime)
		#latestArDir=ardDirs[-1]
		#print "\nardDirs:", ardDirs
		#print "latestArDir:", latestArDir
		#print
		#latestExport=latestArDir + "/export/session.wav"
		latestExport = "/home/jeremy/dev/warp/audio.wav"
		aviWSoundPath = retimeDirPath + "/" + baseOut + "_wSound.avi"
		cmd="ffmpeg -i " + latestExport + " -i " + aviNoSoundPath + \
			" -codec copy -shortest " + aviWSoundPath
		print "\nExecuting:", cmd, "...\n"
		os.system(cmd)



