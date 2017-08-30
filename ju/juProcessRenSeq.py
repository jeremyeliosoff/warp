#!/usr/bin/python
import sys, os, glob

devDir="/home/jeremy/dev/warp/"
sys.path.append(devDir)

import ut

testDir=devDir + "test/processedRen"
renDir=devDir + "ren/"
sc = 3
loops = 2
fade = 30
sfx = "bmp"

seqRenDirs = []

for arg in sys.argv[1:]:
    if "=" in arg:
        k,v = arg.split("=")
        if k == "sc":
            sc = int(v)
        elif k == "loops":
            loops = int(v)
        elif k == "fade":
            fade = int(v)
        elif k == "sfx":
            sfx = v

    else:
        seqRenDirs.append(arg)


for seqRenDir in seqRenDirs:
    seqRenDirPath = renDir + seqRenDir
    vers = ut.getVersions(seqRenDirPath)
    vers.sort()
    vers.reverse()
    latestVer = vers[0]
    print "seqRenDirPath", seqRenDirPath, ";  latestVer", latestVer
    thisRenSubDir = seqRenDirPath + "/" + latestVer + "/ren/ALL"
    print "thisRenSubDir", thisRenSubDir
    searchTerm = thisRenSubDir + "/ren.ALL*" + sfx
    print "searchTerm", searchTerm
    images = glob.glob(searchTerm)
    images.sort()
    print "images:", images
    
    if not sfx == "jpg":
        jpgBakDir = thisRenSubDir + "/jpgBak"
        ut.mkDirSafe(jpgBakDir)
        cmd = "mv " + thisRenSubDir + "/ren.ALL*jpg " + jpgBakDir
        #print "cmd:", cmd
        ut.exeCmd(cmd)
        imagesJpg = []
        for image in images:
            #srcPathLs = image.split("/")
            #dstPathLs = srcPathLs[:-1] + ["jpgBak"] + srcPathLs[-1]
            #dstPath = "/".join(dstPathLs)
            dest = image[:-3] + "jpg"
            imagesJpg.append(dest)

            cmd = "convert " + image + " -quality 100 -compress lossless " + dest
            #print "cmd:", cmd
            ut.exeCmd(cmd)
        del(images)
        images = imagesJpg
            
    #continue
    #convert ren.ALL.%05d.bmp[2220-2229] -quality 100 -compress lossless test.%05d.jpg
    
    seqRenDirPath = testDir + "/" + seqRenDir
    ut.mkDirSafe(seqRenDirPath)
    imgsDest = []
    for iCur in range(len(images)):
        imgCur = images[iCur]
        print "\nimgCur", imgCur
        thisSc = 1
        if iCur < len(images) - 1:
            thisSc = sc
            imgNext = images[iCur + 1]
        for j in range(thisSc):
            imgDest = (seqRenDirPath + "/" + seqRenDir + ".%05d.jpg") % (iCur * sc + j)
            imgsDest.append(imgDest)
            print "imgDest", imgDest
            if j == 0:
                cmd = "cp " + imgCur + " " + imgDest
            else:
                blendA = (100*j)/sc
                blendB = 100 - blendA
                cmd = "composite -dissolve " + str(blendB) + "x" + str(blendA) + " " + imgCur + " " + imgNext + " " + imgDest
            ut.exeCmd(cmd)

    print "\n"

    for iDest,imgSrc in enumerate(imgsDest[-fade:]):
        imgDest = imgsDest[iDest]
        print "\niDest", iDest, "; imgSrc", imgSrc, "; imgDest", imgDest
        blendA = (100*iDest)/fade
        blendB = 100 - blendA
        imgTmp = seqRenDirPath + "/tmp." + imgDest.split(".")[-1]
        cmd = "composite -dissolve " + str(blendB) + "x" + str(blendA) + " " + imgSrc + " " + imgDest + " " + imgTmp
        ut.exeCmd(cmd)
        cmd = "mv " + imgTmp + " " + imgDest
        ut.exeCmd(cmd)
        cmd = "rm " + imgSrc
        ut.exeCmd(cmd)

    imgsDest = imgsDest[:-fade]

    for iDest,imgSrc in enumerate(imgsDest):
        for loopN in range(loops):
            imgDest = (seqRenDirPath + "/" + seqRenDir + ".%05d.jpg") % (iDest + (loopN + 1) * len(imgsDest))
            cmd = "cp " + imgSrc + " " + imgDest
            #print "cmd:", cmd
            ut.exeCmd(cmd)


    
    seqRenDirPref = seqRenDirPath + "/" + seqRenDir
    print "\n seqRenDir", seqRenDir, "seqRenDirPath", seqRenDirPath, "seqRenDirPref", seqRenDirPref, "\n"
    #cmd = "ffmpeg -start_number 0 -framerate 30 -i " + seqRenDirPref + ".%05d.jpg -b 5000k " +  seqRenDirPref + ".avi"
    #cmd = "ffmpeg -r 30 -start_number 0 -i " + seqRenDirPref + ".%05d.jpg -vcodec huffyuv " + seqRenDirPref + ".avi"
    cmd = "ffmpeg -r 30 -start_number 0 -i " + seqRenDirPref + ".%05d.jpg -vcodec libx264 -b 5000k " + seqRenDirPref + ".avi"
    ut.exeCmd(cmd)



    #cmd = "ffmpeg -r 10 -start_number 2220 -i ren.ALL.%05d.jpg -vcodec huffyuv testHuffyBmp.avi"

