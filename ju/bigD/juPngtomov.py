#!/usr/bin/python
import os, glob

cwd = os.getcwd()

pngPaths = glob.glob(cwd + "/*png")
pngPaths.sort()

links = []
startFr = None
prevFr = None
base = None

for pngPath in pngPaths:
	pathWords = pngPath.split(".")
	fr = int(pathWords[-2])
	if startFr == None:
		base = ".".join(pathWords[:-2])
		print "base:", base
		startFr = fr
		prevFr = fr
	else:
		#print "fr", fr, "prevFr", prevFr
		if fr > prevFr + 1:
			#fillPathWords = pathWords.copy()
			for fillFr in range(prevFr+1, fr):
				pathWords[-2] = "%05d" % fillFr
				fillPath = ".".join(pathWords)
				cmd = "ln -s " + pngPath + " " + fillPath
				links.append(fillPath)
				print "Filling fr", fillFr, ", cmd:", cmd
				os.system(cmd)

		prevFr = fr

fps = os.environ['FPS']
print "fps:", fps
cmd = "ffmpeg -start_number " + str(startFr) + " -framerate " + fps + \
	" -i " + base + ".%05d.png -vcodec libx264 -b 5000k " + base + ".avi"
print "executing:", cmd
os.system(cmd)

print "removing links:", links
for link in links:
	os.system("rm " + link)

print "Done.\n"
