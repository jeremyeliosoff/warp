#!/usr/bin/python
import os, sys

dirs = sys.argv[1:]
#print "dirs", dirs
for dr in dirs:
	files = os.listdir(dr)
	files.sort()
	mid = files[len(files)/2]
	mid = mid.replace("tex", "jpg")
	#print "dr:", dr, "mid:", mid
	print "cp "+ dr+ "/" + mid +" /tmp/mid"
	

