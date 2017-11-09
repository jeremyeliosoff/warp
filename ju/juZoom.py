#!/usr/bin/python
import os, glob, subprocess, sys

def clamp(v, mn, mx):
	return min(mx, max(mn, v))

def mix(a, b, m):
	return a * (1.0-m) + b * m

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

def smoothlaunch(edge0, edge1,  x):
	return min(1.0,2.0*smoothstep(edge0, edge0+(edge1-edge0)*2, x))




newLeafName = None

sfx=""
sc = 1

if len(sys.argv) > 3:
	print "\nUSAGE: juZoom.py"
	sys.exit()
for arg in sys.argv[1:]:
	if arg[:2] == "sc":
		sc = float(arg.split("=")[1])
		print "setting sc to", sc
	elif arg[:3] == "sfx":
		sfx = arg.split("=")[1]
		print "setting sfx to", sfx


yCent = .15

cwd = os.getcwd()
pngPaths = glob.glob(cwd + "/*png")
pngPaths.sort()
info = subprocess.check_output(["identify", pngPaths[0]])
#os.system(sysCmd)
print "info:"
print info

resS = info.split()[2].split("x")
res = (int(resS[0]), int(resS[1]))
print "res from", pngPaths[0] + ":",  res

yofs = res[1] * yCent
i = 1
scStart = 1
scEnd = 2.5
scStartFr = 1600
scEndFr = 3500
#scStartFr = 3333
#scEndFr = 3347
#fadeStartFr = 3180
#fadeEndFr = 3350
fadeStartFr = 3260
fadeEndFr = 3400
cropStr = "%dx%d+%d+%d" % (res[0], res[1], 0, 0)

#xsc = res[0] * scStart
#ysc = res[1] * scStart
#cropStr = "%dx%d+%d+%d" % (xsc, ysc, xsc*(1-scStart), ysc*(1-scStart))

for pngPath in pngPaths:
	leaf = os.path.basename(pngPath)
	leafSpl = leaf.split(".")
	fr = leafSpl[-2]
	#print "leafSpl pre", leafSpl, "sfx", sfx
	leafSpl[-3] += sfx
	#print "leafSpl pos", leafSpl, "sfx", sfx
	leaf = ".".join(leafSpl)
	
	prog = smoothlaunch(scStartFr, scEndFr, fr)
	frSc = mix(scStart, scEnd*scStart, prog)
	i += 1
	print "cropStr", cropStr
	fadeFl = smoothlaunch(fadeStartFr, fadeEndFr, fr)
	fade = str(int(100*fadeFl*fadeFl))
	cmd = "convert " + pngPath + (" -distort ScaleRotateTranslate '%d,%d %f 0' -crop " % (res[0]/2, res[1]*yCent, frSc)) + cropStr + " -brightness-contrast -" + fade + ",-" + fade + " -resize " + str(100*sc) + "% zm/" + leaf

	#print "fr", fr, ("prog %.2f" % prog), ":", "*"*int(100*prog)
	print "fr", fr, "prog", prog, ":", cmd
	os.system(cmd)

