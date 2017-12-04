#!/usr/bin/python
import os, glob, subprocess, sys

if "-h" in sys.argv: # 
	print "\nUSAGE: juMakeFinalMov.py [-n (no sound)] [-k (keep link dir)]\n"
	sys.exit()

parentDir = os.getcwd()
aviNoSoundPath = parentDir + "/cigarette_noSound.avi"
aviWSoundPath = parentDir + "/cigarette.avi"

if "-l" in sys.argv: # Do link system
	print "\nDoing avi generation...\n"
	lndir = parentDir + "/links"
	if not os.path.exists(lndir):
		os.makedirs(lndir)


	# Make links to the frames in the subdirectory for each section.
	fr = 0
	for subdir in ["title", "preWarp", "retime", "credits"]:
		pngs = glob.glob(parentDir + "/" + subdir + "/*png")
		pngs.sort()
		for png in pngs:
			cmd = "ln -s " + png + " " + lndir + "/cigarette.%05d.png" % fr
			print "Executing:", cmd
			os.system(cmd)
			fr += 1



	# Make movie links
	cmd = "ffmpeg -framerate 30 -i " + lndir + \
		"/cigarette.%05d.png -vcodec libx264 -b 5000k " + aviNoSoundPath
	print "\nExecuting:", cmd, "...\n"
	os.system(cmd)

	if "-k" in sys.argv: # -k means keep links
		print "\n-k specified: not removing links."
	else:
		# Delete the links
		cmd = "rm -fr " + lndir
		print "\nExecuting:", cmd
		os.system(cmd)

else:
	pngs = glob.glob(parentDir + "/title/*png")
	pngs += glob.glob(parentDir + "/preWarp/*png")
	pngs += glob.glob(parentDir + "/retime/*png")
	pngs += glob.glob(parentDir + "/credits/*png")
	fr = len(pngs)

	print "n frames:", fr

	if "-n" in sys.argv: # -n means only add sound
		pngs = glob.glob(parentDir + "/" + subdir + "/*png")
		print "\nSkipping avi generation, just adding sound...\n"
	else: # concat preexisting avis
		cmd="ffmpeg -f concat -i concatLs.txt -c copy " + aviNoSoundPath
		print "\nExecuting:", cmd, "...\n"
		os.system(cmd)





# Add sound to video.
#
dur = float(fr)/30
rawSoundWithMusicPath = "/home/jeremy/dev/warp/audio/rawSoundWithMusic.wav"
cmd="ffmpeg -i " + rawSoundWithMusicPath + " -i " + aviNoSoundPath + \
" -codec copy -t " + str(dur) + " " + aviWSoundPath
print "\nExecuting:", cmd, "...\n"
os.system(cmd)

print "\nDone.  Movie with sound:", aviWSoundPath, "\n"

