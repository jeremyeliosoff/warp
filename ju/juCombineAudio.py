#!/usr/bin/python
import os, glob, subprocess, sys

# AUDIO

audioDir = "/home/jeremy/dev/warp/audio"

# Append silence to raw sound.
concatRawWithSilencePath = audioDir + "/concatRawWithSilence.txt"
silent53sPath= audioDir + "/silent53s.wav"
with open(concatRawWithSilencePath, 'w') as f:
	f.write("""file 'silent1p6s.wav'
file 'rawAudio_startSec2_fade55_75.wav'
file 'silent53s.wav'""")
	
rawSoundThenSilencePath = audioDir + "/rawSoundThenSilence.wav"
cmd="ffmpeg -f concat -i " + concatRawWithSilencePath + " -c copy " + rawSoundThenSilencePath
print "\nExecuting:", cmd, "...\n"
os.system(cmd)

# Prepend latest music with silence.
concatSilenceWithMusicPath = audioDir + "/concatSilenceWithMusic.txt"
with open(concatSilenceWithMusicPath, 'w') as f:
	f.write("""file 'silent1p6s.wav'
file 'silent53s.wav'
file 'music.wav'""")
	
silenceThenMusicPath = audioDir + "/silenceThenMusic.wav"
cmd="ffmpeg -f concat -i " + concatSilenceWithMusicPath + " -c copy " + silenceThenMusicPath
print "\nExecuting:", cmd, "...\n"
os.system(cmd)

# Overlay on raw audio
rawSoundWithMusicPath = audioDir + "/rawSoundWithMusic.wav"
cmd="ffmpeg -i " + rawSoundThenSilencePath + " -i " + silenceThenMusicPath + " -filter_complex amerge -ac 2 -c:a libmp3lame -q:a 4 " + rawSoundWithMusicPath
print "\nExecuting:", cmd, "...\n"
os.system(cmd)

print "\nDone creating combined audio file:", rawSoundWithMusicPath, "\n"

