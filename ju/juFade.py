#!/usr/bin/python
import os, glob, subprocess, sys

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

def smoothpulse(edge0, edge1, edge2, edge3, x):
	return smoothstep(edge0, edge1, x) * (1-smoothstep(edge2, edge3, x))


if not len(sys.argv) == 7:
	print "\nUSAGE: juFade.py image fadeDur totalDur prePad postPad basename\n"
	sys.exit()

image, fadeDur, totalDur, prePad, postPad, basename = sys.argv[1:]
prePad=int(prePad)
postPad=int(postPad)
fadeDur=int(fadeDur)
totalDur=int(totalDur)

if not os.path.exists("fade"):
	os.makedirs("fade")

for i in range(totalDur):
	k = 1-smoothpulse(prePad, prePad+fadeDur, totalDur-fadeDur-postPad, totalDur-postPad, i)
	k = str(int(100*k))
	imgToUse = image
	if "SEQ" in image:
		imgToUse = image.replace("SEQ", ".%05d.png" % i)
		print "imgToUse", imgToUse
	cmd = "convert " + imgToUse +  " -brightness-contrast -" + str(k) + ",-" + str(k) + " fade/" + basename + (".%05d.png" % i)
	print "executing:", cmd
	os.system(cmd)

