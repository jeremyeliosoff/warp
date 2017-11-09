#!/usr/bin/python
import os, sys

groups = sys.argv[1:]
for group in groups:
	dr,rng = group.split(":")
	mn,mx = rng.split("-")
	mn = int(mn)
	mx = int(mx)
	files = os.listdir(dr)
	files.sort()
	print "\n#dr", dr, "mn", mn, "mx", mx
	for f in files:
		words = f.split(".")
		if len(words) > 2:
			num = words[-2]
			try:
				num = int(num)
			except:
				continue
			if num < mn or num > mx:
				print "rm " + dr + "/" +f
	

