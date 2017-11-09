#!/usr/bin/python

import os, pprint, glob

seqFiles = glob.glob("*jpg")
seqFiles.sort()
print "seqFiles", seqFiles
components = seqFiles[0].split(".")
root = components[0]
sfx = components[-1]

zigDir = "zig"
if not os.path.isdir(zigDir):
    os.makedirs(zigDir)


oldToNew = {}
for seqFile in seqFiles:
    oldToNew[seqFile] = []

iSrc = 0
incr = -1
nFr = 30
for iDst in range(nFr):
    #dstFile = root + "_zig." + ("%05d" % iDst) + "." + sfx
    dstFile = root + "." + ("%05d" % iDst) + "." + sfx
    print "\niSrc", iSrc, "len(seqFiles)", len(seqFiles)
    print "dstFile", dstFile
    srcFile = seqFiles[iSrc]
    print "srcFile", srcFile
    oldToNew[srcFile].append(dstFile)
    if iSrc == (len(seqFiles)-1) or iSrc == 0:
        incr *= -1
    iSrc += incr

print "\n oldToNew:",
pprint.pprint(oldToNew)

for src,dsts in oldToNew.items():
    for dst in dsts:
        cmd = "cp " + src + " " + zigDir + "/" + dst
        print "cmd:", cmd
        os.system(cmd)
    





