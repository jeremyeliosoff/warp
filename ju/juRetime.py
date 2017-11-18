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
fpsStart = 30
fpsEnd = 5

#for i in range(frange):


if len(sys.argv) == 1 or len(sys.argv) > 4:
	print "\nUSAGE: juRetime.py basename [basenameOut]\n"
	sys.exit()


baseIn = sys.argv[1]

if len(sys.argv) == 3:
	baseOut = sys.argv[2]
else:
	baseOut = baseIn

basenameIn = baseIn + ".%05d.png"
basenameOut = baseOut + ".%05d.png"
#while frSrc < frange:
frSrc = frStart
while frSrc < frEnd:
	prog = float(frSrc)/(frange-1)
	incr = mix(1, float(fpsEnd)/fpsStart, prog)

	i = 0
	for fpsGrp in fpsGrps:
		#print "fpsGrp[0]", fpsGrp[0]
		if i >= (len(fpsGrps)-1) or fpsGrps[i+1][0] > frSrc:
			break
		i += 1
	prog = smoothstep(fpsGrp[0], fpsGrp[1], frSrc)
	fpsPrev = fpsStart if i == 0 else fpsGrps[i-1][2]
	fpsNext = fpsGrp[2]
	#print "fpsPrev", fpsPrev, "fpsNext", fpsNext, "prog", prog
	fps = mix(fpsPrev, fpsNext, prog)
	incr = float(fps)/fpsStart

	frSrc += incr
	frA, mixB = divmod(frSrc, 1)
	frB = frA + 1
	mixB = frSrc % 1
	mixA = 1.0 - mixB
	imgA = basenameIn % frA
	imgB = basenameIn % frB

	while (not os.path.exists(imgA)) and frA <= frEnd:
		print "\t!!!!", imgA, "does not exist! checking next frame..."
		frA += 1
		imgA = basenameIn % frA

	while (not os.path.exists(imgB)) and frB <= frEnd:
		print "\t!!!!", imgB, "does not exist! checking next frame..."
		frB += 1
		imgB = basenameIn % frB

	if not os.path.exists("retime"):
		os.makedirs("retime")

	imgOut = "retime/" +  basenameOut % frOut
	cmd = "composite -dissolve " + str(int(100*mixA)) + "x" + \
		str(int(100*mixB)) + " " + imgA + " " + imgB + " " + imgOut
	print "frOut", frOut, "frSrc", frSrc, ":", cmd
	#print "frOut", frOut, "i", i, "fpsPrev", fpsPrev, "fpsNext", fpsNext, "fps", fps, "incr", incr, "frSrc", frSrc
	os.system(cmd)
	frOut += 1


