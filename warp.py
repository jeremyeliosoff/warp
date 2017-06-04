#!/usr/bin/python
import os, genData, ut, time, pprint, glob
from Tkinter import *
import Tkinter
import PIL
from PIL import ImageTk, Image
from tkColorChooser import askcolor              

parmPath = ut.projDir + "/parms"


class warpUi():
    def rebuildUI(self):
        print "reloading........"
        self.refreshParms()
        ut.exeCmd("killall warp.py; /home/jeremy/dev/warp/warp.py")
        
    def saveDics(self):
        print "Saving dics..."
        genData.pickleDump(self.seqDataVDir + "/tidToSids", self.tidToSids)
        genData.pickleDump(self.seqDataVDir + "/sidToTid", self.sidToTid)

    def delDics(self):
        print "Saving dics..."
        ut.exeCmd("rm " + self.seqDataVDir + "/tidToSids")
        ut.exeCmd("rm " + self.seqDataVDir + "/sidToTid")
        
    def flushDics(self):
        print "Flushing dics"
        self.tidToSids = None
        self.sidToTid = None
        self.nextSid = 0
        
    def refreshParms(self):
        #print "parmDic", self.parmDic
        for k,v in self.parmDic.parmDic.items():
            thisDic = self.parmDic.parmDic[k]
            #print "\nIN refreshParms: k", k, "thisDic", thisDic
            # Below is just so we don't make errors before all the
            # ui is built - a bit unsatisfying.
            if "uiElement" in thisDic.keys() and not thisDic["type"] == "clr":
                thisDic["val"] = thisDic["uiElement"].get()
        self.saveParmDic()

    def btn_getColor(self, args):
        k,c = args
        print "ZZZZZZZZZZZ in btn_getColor-- k:", k, ", c:", c
        c = self.parmDic(k)
        hx = ut.rgb_to_hex(c)
        print "c:", c
        print "hx:", hx
        color = askcolor(color=hx) 
        print "color", color
        if color:
            clrInt = color[0]
            clrDec = ut.rgb_int_to_dec(clrInt)
            print "clrDec", clrDec
            self.setVal(k, clrDec)
            postC = self.parmDic(k)
            print "postC", postC
            self.parmDic.parmDic[k]["uiElement"].configure(bg=color[1])
    
    def makeParmUi(self, startRow):
        row = startRow
        print "\n\n************** parmLs", self.parmDic.parmLs
        for k,dic in self.parmDic.parmLs: # Recall: parmLs = [("parmName", {'key':val...}]
            thisParmDic = self.parmDic.parmDic[k]
            #print "-------------IN makeParmUi, k:", k, ", thisParmDic:", thisParmDic
            
            if "hidden" in thisParmDic.keys() and thisParmDic["hidden"] == "True":
                print "HIDDEN, skipping..."
                continue
            lab = Label(self.frameParm, text=k)
            lab.grid(row=row, column=0, sticky=E)


            if thisParmDic["type"] == "clr":
                clrTuple = self.parmDic(k)
                hx = ut.rgb_to_hex(clrTuple)
                ent = Button(self.frameParm, width=10, bg=hx,command=lambda args=(k,clrTuple): self.btn_getColor(args))
            else:
                ent = Entry(self.frameParm)
            ent.grid(row=row, column=1, sticky=W)
            thisParmDic["uiElement"] = ent
            #print "-------- ent:", ent

            if not thisParmDic["type"] == "clr":
                sv = StringVar()
                # TODO: How does this work?
                sv.trace("w", lambda name, index, mode, sv=sv: self.refreshParms())

                thisParmDic["uiElement"].configure(textvariable=sv)
                thisParmDic["uiElement"].insert(0, str(thisParmDic["val"]))

            row += 1
        return row
        

    def positionWindow(self):
        w = 1500 # width for the Tk root
        h = 750 # height for the Tk root

        # get screen width and height
        ws = self.root.winfo_screenwidth() # width of the screen
        hs = self.root.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = ws/8
        y = hs/8
        #x = ws - (w/2)
        #y = hs - (h/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))


    def loadImagesBak(self):
        print "ya"
        
    def getDbImgParmNames(self):
        dbImgNames = []
        root = "dbImg"
        for k in self.parmDic.parmDic.keys():
            if k[:len(root)] == root:
                dbImgNames.append(k)
        print "\n\n XXXXXX dbImgNames:", dbImgNames
        dbImgNames.sort()
        return dbImgNames


    def loadImages(self):
        # TODO: I expect at least looking up thisImgPath from ut
        # is wrong -- I think they all get overwritten.

        for k in self.getDbImgParmNames():
            lev = self.parmDic("lev_" + k)
            path = self.getDebugDirAndImg(self.parmDic(k), lev)[1]
            print "BBBBBBb k:", k, ", path", path
            self.images[k]= {"path":path}


        imgPath = self.getSourceImgPath()
        self.images["source"] = {"path":imgPath}
        self.images["ren"] = {"path":imgPath.replace("/seq/","/ren/")}

        self.images["anim"] = {"pImg":self.staticImages["play"]}
        self.images["rec"] = {"pImg":self.staticImages["recOff"]}
        #self.images["rew"] = {"path":self.images["rew"]["path"]}

        print "images:"
        for i,k in self.images.items():
            print i, k

        for img in self.images.keys():
            if not img in (self.staticImageNames + self.varyingStaticImageNames):
                path = self.images[img]["path"]
                print "000000000 img:", img
                print "Checking existence of", path
                #if os.path.exists(path):
                self.images[img]["pImg"] = self.safeLoad(path)
                #else:
                #    # this is a dud/placeholder image.
                #    self.images[img]["pImg"] = self.safeLoad(self.staticImages["play"])

        image = self.images["source"]["pImg"]
        self.res = (image.width(), image.height())

        print "\n\nVVVVVVVVVVv self.images:"
        for k,v in self.images.items():
            print k, v




    def refreshPhotoImages(self):
        # TODO you shouldn't have to reload ALL images eg. play, pause - maybe
        # keep those images "on hand" as PhotoImages that you switch between
        for k,thisDic in self.images.items():
            if not k in (self.staticImageNames + self.varyingStaticImageNames):
                #print "IN refreshPhotoImages: loading", thisDic["path"]
                pImg = self.safeLoad(thisDic["path"])
                if k in self.images.keys():
                    self.images[k]["pImg"] = pImg
                else:
                    self.images[k]= {"pImg":pImg}


    def makeImgButton(self, name, frameParent):
        print "name: ", name
        pImg = self.images[name]["pImg"]
	thisButton = Button(frameParent, image=pImg, command=lambda:self.imgButCmd())
	self.images[name]["button"] = thisButton
        return thisButton


    def refreshButtonImages(self): 
        self.refreshPhotoImages()

        for butName,butDic in self.images.items():
            #print "butName", butName, "butDic:", butDic
            if "button" in butDic.keys():
                butDic["button"].configure(image=butDic["pImg"])

        if self.parmDic("anim") == 1:
            self.images["anim"]["button"].configure(image=self.staticImages["pause"])
        else:
            self.images["anim"]["button"].configure(image=self.staticImages["play"])

        if self.record:
            self.images["rec"]["button"].configure(image=self.staticImages["recOn"])
        else:
            self.images["rec"]["button"].configure(image=self.staticImages["recOff"])


    def imgButCmd(self):
        self.refreshParms()
        self.updateCurImg(forceRecord=True)
        self.updateDebugImg()

    def setFrAndUpdate(self, fr):
        self.setStatus("busy")
        self.setVal("fr", fr)
        self.refreshParms()
        self.updateDataDirs()
        self.updateCurImg()
        self.updateDebugImg()
        Tk.update_idletasks(self.root)
        

    def returnCmd(self):
        self.frameMaster.focus_set()
        self.refreshParms()
        self.updateCurImg()

    def stepBackButCmd(self):
        self.setFrAndUpdate(self.parmDic("fr") - 1)

    def stepFwdButCmd(self):
        self.setFrAndUpdate(self.parmDic("fr") + 1)

    def rewButCmd(self):
        self.setFrAndUpdate(self.parmDic("frStart"))

    def ffwButCmd(self):
        self.setFrAndUpdate(self.parmDic("frEnd"))


    def animButCmd(self):
        anim = self.parmDic("anim")
        if anim == 0:
            self.setVal("anim", 1)
            self.refreshButtonImages()
            self.timeStart = time.time()
            self.frStartAnim = self.parmDic("fr")
            self.updateCurImg()
        else:
            self.setVal("anim", 0)
            self.refreshButtonImages()
        print "Pressed anim button, anim set to", anim
        self.refreshParms()

    def recButCmd(self):
        self.record = not self.record
        print "recButCmd; self.record =", self.record
        self.refreshButtonImages()

    def toggleDoRenCv(self):
        if self.chk_doRenCv_var.get() == 1:
            val = 0
        else:
            val = 1
        self.chk_doRenCv_var.set(val)
        self.setVal("doRenCv", val)

    def saveParmDic(self):
        #print "\n\n\n INSIDE saveParmDic"
        with open(parmPath, 'w') as f:
            for k in self.parmDic.parmLs:
                parm = k[0]
                f.write(parm + "\n")
                thisDic = self.parmDic.parmDic[parm]
                #print "k", k, "thisDic", thisDic
                keys = thisDic.keys()
                keys.sort()
                for attr in keys:
                    if not attr == "uiElement":
                        f.write(attr + " " + str(thisDic[attr]) + "\n")
                f.write("\n")

    def updateDebugImg(self):
        #print " -- IN updateDebugImg"
        for i in range(2):
            img = self.parmDic("dbImg" + str(i+1))
            lev = self.parmDic("lev_dbImg" + str(i+1))
            dbImgPath = self.getDebugDirAndImg(img, lev)[1]
            self.images["dbImg" + str(i+1)]["path"] = dbImgPath
            self.setVal("dbImg" + str(i+1), img)
            #print "dbImgPath", dbImgPath
	self.refreshButtonImages()

    # TODO: I sense that this is done too much ie. every frame, need only do when img is selected.
    def getSourceImgPath(self):
        imageTitle = self.parmDic("image")
        fr = self.parmDic("fr")
        seqImages = os.listdir(ut.seqDir + "/" + imageTitle)
        seqImages.sort()
        mx = -100
        mn = 10000000
        for img in seqImages:
            if img == "bak" or not "." in img:
                continue
            #print "--------img", img
            imgSplit = img.split(".")
            thisFr = int(imgSplit[-2])
            if thisFr < mn:
                mn = thisFr
            if thisFr > mx:
                mx = thisFr

        fr = ut.clamp(fr, mn, mx)
        self.seqStart = mn
        #self.frStartAnim = fr
        self.seqEnd = mx
        self.setVal("fr", fr)

        imgWithFrame = ".".join(imgSplit[:-2]) + (".%05d." % fr) + imgSplit[-1]
        return ut.seqDir + "/" + self.parmDic("image") + "/" + imgWithFrame

    def updateCurImg(self, forceRecord=False):
        imgPath = self.getSourceImgPath()
        #self.images["source"]["path"] = ut.seqDir + "/" + self.parmDic("image") + "/" + imgWithFrame
        self.images["source"]["path"] = imgPath
        self.images["ren"]["path"] = imgPath.replace("/seq/","/ren/")
        self.refreshParms()
        #print "\n\n------- self.images", self.images
        print "\n\n self.record", self.record

        ut.exeCmd("rm " + genData.outFile)
        genData.pOut("\nPRE genData")

        ######## THIS IS WHERE DATA GETS GENERATED ########
        if self.record or forceRecord:
            genData.pOut("doing genData")
            reload(genData)
            self.setStatus("busy", "Doing genData...")
            genData.genData(self)
            print "\nDone genData\n\n"
            self.setStatus("idle")
        else:
            genData.pOut("skipping genData")
        ###################################################
        

        #pp = pprint.pformat(self.sidToTid)
        #genData.pOut("Post genData, sidToTid", pp)

	self.refreshButtonImages()
        image = self.images["source"]["pImg"]
        self.res = (image.width(), image.height())
        print "--------XXX PRE setStatus"
        self.setStatus("idle")
        print "--------XXX POSt setStatus"


    # This is a horrendous mess - must be a cleaner way to get debug num + lev num
    def getImgDebug1(self, selection):
        if not selection == "----":
            self.getImg(selection, debugNum=1)

    def getImgDebug2(self, selection):
        if not selection == "----":
            self.getImg(selection, debugNum=2)

    def getLevDebug1(self, selection):
        if not selection == "----":
            self.getImg(selection, debugNumLev=1)

    def getLevDebug2(self, selection):
        if not selection == "----":
            self.getImg(selection, debugNumLev=2)



    def getImg(self, selection, debugNum=None, debugNumLev=None):
        print "\n\n --getImg: selection:",  selection, ", debugNum:", debugNum
        thisImg = selection
        if debugNum:
            self.setVal("dbImg" + str(debugNum), selection)
            self.updateDataDirs()
            self.updateDebugImg()
        elif debugNumLev:
            self.setVal("lev_dbImg" + str(debugNumLev), selection)
            self.updateDataDirs()
            self.updateDebugImg()
        else:
            print "################ setting selection:", selection
            if self.record:
                # Turn off recording so you don't render right away.
                self.recButCmd()
            self.setVal("image", selection)
            self.updateDataDirs()
            self.updateCurImg()
            self.updateDebugImg()

    def menuImgChooser(self, selection):
        self.getImg(selection)
        dataVers = self.getDataVersions()
        print "\n******self.seqDataDir", self.seqDataDir, "self.imgVChooserVar.get()", self.imgVChooserVar.get(), "dataVers", dataVers
        if not self.imgVChooserVar.get() in dataVers:
            latestVer = int(dataVers[0])
            print "\tresetting  latestVer to ", latestVer
            #self.imgVChooserVar.set("v%03d" % latestVer)
            self.imgVChooserVar.set(latestVer)
            self.setVal("dataVer", latestVer)

        self.setVal("frStart", self.seqStart)
        self.setVal("frEnd", self.seqEnd)

    def menuImgVChooser(self, selection):
        verNum = selection
        print "menuImgVChooser: setting dataVer to", verNum
        self.setVal("dataVer", verNum)
        self.updateDataDirs()
        self.updateCurImg()
        self.updateDebugImg()

    def but_imgVNew(self):
        dataVers = self.getDataVersions()
        dataVers.sort()
        print "dataVers"
        print dataVers
        print "dataVers[-1]", dataVers[-1]
        print "dataVers[-1][1:4]", dataVers[-1][1:4]
        nextVerInt = int(dataVers[-1][1:4]) + 1
        nextVer = ("v%03d" % nextVerInt) + self.imgVNewSfx.get()
        ut.mkDirSafe(self.seqDataDir + "/" + nextVer)
        self.setVal("dataVer", nextVer)
        self.rebuildUI()


    def chk_doRenCv_cmd(self):
        val = self.chk_doRenCv_var.get()
        print "Setting doRenCv to:", val
        self.setVal("doRenCv", val)

    def setVal(self, parmStr, val):
        if "uiElement" in self.parmDic.parmDic[parmStr]:
            uiElement = self.parmDic.parmDic[parmStr]["uiElement"]
            if not self.parmDic.parmDic[parmStr]["type"] == "clr":
                uiElement.delete(0, END)
                uiElement.insert(0, str(val))
        valStr = str(val)
        #print "valStr pre", valStr
        if type(val) in [type(()), type([])]:
            valStr = valStr[1:-1].replace(' ','')
        #print "valStr pos", valStr
        print "setVal: setting parmDic[" + parmStr + "] to", valStr
        self.parmDic.parmDic[parmStr]["val"] = valStr
        self.refreshParms()

    def makeFramesDataDir(self, fr=None):
        if not fr:
            fr = self.parmDic("fr")
        frameDir = self.framesDataDir + ("/%05d" % fr)
        ut.mkDirSafe(frameDir)
        return fr, frameDir

    def getDataVersions(self):
        dataVers = [f for f in os.listdir(self.seqDataDir) if re.match('v[0-9][0-9][0-9]*', f)]
        dataVers.sort()
        dataVers.reverse()

        # Make v000 dir if there is none.
        if dataVers == []:
            ut.mkDirSafe(self.seqDataDir + "/v000")
            dataVers = ["v000"]

        return dataVers

    def updateDataDirs(self):
        self.seqDataDir = ut.dataDir + "/" + self.parmDic("image")
        ut.mkDirSafe(self.seqDataDir)
        #self.seqDataVDir = self.getLatestVersion()
        self.seqDataVDir = self.seqDataDir + self.parmDic("dataVer")
        self.framesDataDir = self.seqDataVDir + "/frames"

    def getDebugDirAndImg(self, debugInfo, lev):
        fr = self.parmDic("fr")
        levDir = self.seqDataVDir + "/debugImg/" + debugInfo + "/" + lev # TODO: v00
        imgPath = levDir + ("/" + debugInfo + "." + lev + ".%05d.jpg" % fr)
        return levDir,imgPath

    def safeLoad(self, path):
        if os.path.exists(path):
            img = ImageTk.PhotoImage(Image.open(path))
        else:
            img = self.staticImages["error"]
        return img

    def getOfs(self, fr=None):
        if fr == None:
            fr = self.parmDic("fr")
        return fr/float(self.parmDic("frPerCycle"))

    def getOfsWLev(self, lev, fr=None):
        return self.getOfs(fr) + float(lev)/self.parmDic("nLevels")

    def setStatus(self, typ, msg=""):

        defaultBg = self.root.cget('bg')
        fgClr= {
                "error":"black",
                "idle":"black",
                "busy":"red"}

        bgClr= {
                "error":"red",
                "idle":defaultBg,
                "busy":defaultBg}
        # You can't go directly from error to idle.
        if not (self.status == "error" and typ == "idle"):
            if typ == "idle":
                msg = "Idle"
            self.status = typ
            self.labelStatus.configure(text=msg, bg=bgClr[typ], fg=fgClr[typ])
            Tk.update_idletasks(self.root)



    def __init__(self):
        # Needed for pickling.
        lim = sys.getrecursionlimit()
        sys.setrecursionlimit(lim*1000)

        self.getImgDebugFunctions = {
                "name":[self.getImgDebug1, self.getImgDebug2],
                "lev":[self.getLevDebug1, self.getLevDebug2]
        }
        self.parmDic = ut.parmDic(parmPath)
        print "\n\n\n********** parmDic2"
        print self.parmDic
        self.inSurfGridPrev = None
        self.setVal("anim", 0)
        nLevels = self.parmDic("nLevels")
        self.updateDataDirs()
        self.nextSid = 0
        self.tidToSids = None
        self.sidToTid = None
        self.root = Tk()
        self.root.wm_title("WARP")
        self.positionWindow()
        self.gridJt = None
        self.gridLevels = None
        self.gridOut = None
        self.record = False
        self.seqEnd = -100
        self.seqStart = 10000000
        self.timeStart = time.time()

        sourceImages = os.listdir(ut.imgIn)
        sourceImages.sort()


        # TODO e needed?
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<Return>', lambda e: self.returnCmd())
        self.root.bind('<Left>', lambda e: self.stepBackButCmd())
        self.root.bind('<Right>', lambda e: self.stepFwdButCmd())
        self.root.bind('<Control-Left>', lambda e: self.rewButCmd())
        self.root.bind('<Control-Right>', lambda e: self.ffwButCmd())
        self.root.bind('<space>', lambda e: self.animButCmd())
        self.root.bind('<r>', lambda e: self.recButCmd())
        self.root.bind('<c>', lambda e: self.toggleDoRenCv())
        self.root.bind('<x>', lambda e: self.imgButCmd())
        #self.root.bind('<c>', lambda e: if self.chk_doRenCv_var.get() == 1 : self.chk_doRenCv_var.set(0) else self.chk_doRenCv_var.set(1))
        #self.root.bind('<c>', lambda e: self.chk_doRenCv())

        #self.chk_doRenCv_var.set(self.parmDic("doRenCv"))

        # Load images.
        self.staticImageNames = ["play", "pause", "rew", "stepBack", "stepFwd", "ffw", "recOn", "recOff", "error"]
        self.varyingStaticImageNames = ["anim", "rec"]
        self.staticImages = {}
        base = ut.imgDir + "/controls/"
        for name in self.staticImageNames:
            self.staticImages[name] = ImageTk.PhotoImage(Image.open(base + name + ".jpg"))
        self.images = {}
        self.loadImages()


        self.frameMaster = Frame(self.root)
	self.frameMaster.grid()

        self.frameParmAndControls = Frame(self.frameMaster)
        self.frameParmAndControls.grid(row=0, column=0, sticky=N)

        self.frameLeft = Frame(self.frameParmAndControls)
        self.frameLeft.grid(row=0, column=0, sticky=NW)
        row = 0

        self.frameTopControls = Frame(self.frameLeft)
        self.frameTopControls.grid(row=0, sticky=NW)

        self.frameParm = Frame(self.frameLeft)
        self.frameParm.grid(row=1, sticky=N)
        row = 0

        # Status label
	self.labelStatus = Label(self.frameTopControls, justify="left")
	self.labelStatus.grid(row=row, column=0, sticky=W)
        self.status = "idle"
        self.setStatus("idle")
        row +=1

        # Recreate UI button
	self.but_rebuildUi = Button(self.frameTopControls, text="Recreate UI", command=lambda:self.rebuildUI())
	self.but_rebuildUi.grid(row=row, column=0, sticky=EW)
        row +=1

        # Dics button
        self.frameDics = Frame(self.frameTopControls)
        self.frameDics.grid(row=row, sticky=N)
        row +=1

	self.but_flushDics = Button(self.frameDics, text="Flush dics", command=lambda:self.flushDics())
	self.but_flushDics.grid(row=0, column=0, sticky=W)

	self.but_delDics = Button(self.frameDics, text="Delete saved dics", command=lambda:self.delDics())
	self.but_delDics.grid(row=0, column=1, sticky=W)

	self.but_saveDics = Button(self.frameDics, text="Save dics", command=lambda:self.saveDics())
	self.but_saveDics.grid(row=0, column=2, sticky=W)


        # Do renCv checkbox

        self.chk_doRenCv_var = IntVar()
        self.chk_doRenCv_var.set(self.parmDic("doRenCv"))
        self.chk_doRenCv = Checkbutton(self.frameTopControls, text="Do renCv", variable=self.chk_doRenCv_var, command=self.chk_doRenCv_cmd)
	self.chk_doRenCv.grid(row=row, column=0, sticky=W)
        row +=1


        # Make parm UI
        row = self.makeParmUi(row)


        # Image chooser
	self.imgLabel = Label(self.frameParm, text="image")
        self.imgLabel.grid(row=row, sticky=E)

        sourceSequences = os.listdir(ut.seqDir)
        if "bak" in sourceSequences: # Skip bak dir
            sourceSequences.remove("bak")
        sourceSequences.sort()
        self.imgChooserVar = StringVar(self.frameParm)
        self.imgChooserVar.set(self.parmDic("image"))
        self.imgChooser = OptionMenu(self.frameParm, self.imgChooserVar, *sourceSequences, command=self.menuImgChooser)
        self.imgChooser.grid(row=row, column=1, sticky=EW)
        row += 1

        # Data version chooser

	self.imgVLabel = Label(self.frameParm, text="dataVersion")
        self.imgVLabel.grid(row=row, column=0, sticky=E)


        self.frameImgV = Frame(self.frameParm)
        self.frameImgV.grid(row=row, column=1, sticky=EW)
        self.imgVChooserVar = StringVar(self.frameImgV)
        self.imgVChooserVar.set(self.parmDic("dataVer"))
        print "--- self.imgVChooserVar.get()", self.imgVChooserVar.get()
        dataVers = self.getDataVersions()
        print "\n dataVers:", dataVers
        self.imgVChooser = OptionMenu(self.frameImgV, self.imgVChooserVar, *dataVers, command=self.menuImgVChooser)
        self.imgVChooser.grid(row=0, column=0, sticky=W)

	#self.imgVNewLabel = Label(self.frameImgV, text="makeNew")
	self.imgVNew = Button(self.frameImgV, text="Make New", command=lambda:self.but_imgVNew())
        self.imgVNew.grid(row=0, column=1, sticky=E)

	self.imgVNewSfx = Entry(self.frameImgV, width=12)
        self.imgVNewSfx.grid(row=0, column=3, sticky=E)
        #self.imgVNewLabel.grid(row=0, column=1)
        row += 1




        # Playback controls.
        framePlaybackControls = Frame(self.frameParmAndControls)
        framePlaybackControls.grid(row=row, sticky=S) # Not convinced sticky does anything here.


        column = 0
        # Rew
	thisButton = Button(framePlaybackControls, image=self.staticImages["rew"], command=lambda:self.rewButCmd())
        thisButton.grid(row=0, column=column)
        column += 1


        # Step back
	thisButton = Button(framePlaybackControls, image=self.staticImages["stepBack"], command=lambda:self.stepBackButCmd())
        thisButton.grid(row=0, column=column)
        column += 1


        # Play
        if self.parmDic("anim") == 1:
            img = self.staticImages["pause"]
        else:
            img = self.staticImages["play"]
	thisButton = Button(framePlaybackControls, image=img, command=lambda:self.animButCmd())
	self.images["anim"]["button"] = thisButton
        thisButton.grid(row=0, column=column)
        column += 1

        # Step fwd
	thisButton = Button(framePlaybackControls, image=self.staticImages["stepFwd"], command=lambda:self.stepFwdButCmd())
        thisButton.grid(row=0, column=column)
        column += 1


        # Ffw
	thisButton = Button(framePlaybackControls, image=self.staticImages["ffw"],
                    command=lambda:self.ffwButCmd())
        thisButton.grid(row=0, column=column)
        column += 1


        # Rec
        if self.record:
            img = self.staticImages["recOn"]
        else:
            img = self.staticImages["recOff"]
	thisButton = Button(framePlaybackControls, image=img, command=lambda:self.recButCmd())
	self.images["rec"]["button"] = thisButton
        thisButton.grid(row=0, column=column)
        column += 1


        # Make picture (button) UI
        self.frameImg = Frame(self.frameMaster)
        self.frameImg.grid(row=0, column=1)
        row = 0

        thisLabel = Label(self.frameImg, text="source")
        thisLabel.grid(row=row)
        thisButton = self.makeImgButton("source", self.frameImg)
        thisButton.grid(row=row+1)


        thisLabel = Label(self.frameImg, text="ren")
        thisLabel.grid(row=row,column=1)
        thisButton = self.makeImgButton("ren", self.frameImg)
        thisButton.grid(row=row+1, column=1)
        row +=2


        # Debug images.
        path = self.seqDataVDir + "/debugImg"
        print "=========== PATH", path
        if os.path.exists(path):
            sourceImages = os.listdir(path)
        else:
            sourceImages = []
        if sourceImages == []:
            sourceImages = ["----"]

        sourceImages.sort()

        self.dbMenus = {}
        col = 0
        for dbImgName in self.getDbImgParmNames():
            print "\\\\\\\\\\\\ col", col, "dbImgName", dbImgName
            frameDbParm = Frame(self.frameImg)
            thisButton = self.makeImgButton(dbImgName, frameDbParm)
            thisButton.grid()
            
            frameDbMenus = Frame(frameDbParm)
            frameDbMenus.grid(row=1)
            varName = StringVar(self.frameParm)
            # TODO: Replace with parmDic(dbImgName) -- look for other instances that need similar replacement.
            varName.set(self.parmDic.parmDic[dbImgName]["val"])
            imgChooser = OptionMenu(frameDbMenus, varName, *sourceImages, command=self.getImgDebugFunctions["name"][col])
            imgChooser.grid()

            varLev = StringVar(self.frameParm)
            varLev.set(self.parmDic("lev_" + dbImgName))
            levs = ["lev%02d" % i for i in range(self.parmDic("nLevels"))] + ["ALL"]
            levChooser = OptionMenu(frameDbMenus, varLev, *levs, command=self.getImgDebugFunctions["lev"][col])
            levChooser.grid(row=0,column=1)

            # TODO: varName and varLev are not yet used.
            self.dbMenus[dbImgName] = {"menu":imgChooser, "varName":varLev, "varLev":varLev}
            frameDbParm.grid(row=row,column=col)
            col += 1


        # Update menu-dependent images to reflect current selection.
        self.getImg(self.parmDic("image")) 
        while True:
            anim = self.parmDic("anim")
            if anim == 1:
                fr = self.parmDic("fr")
                frPerCycle = self.parmDic("frPerCycle")
                nLevels = self.parmDic("nLevels")
                secondsPassed = time.time() - self.timeStart
                newFr = self.frStartAnim + int(secondsPassed*self.parmDic("fps"))
                #print "frStartAnim:", self.frStartAnim, ", secondsPassed:", secondsPassed, "\tfr", fr, "\tnewFr = ", newFr
                if newFr > fr:        
                    fr = min(fr + 1, newFr)
                    if fr > self.parmDic("frEnd"):
                        if self.parmDic("doRenCv") == 0:
                            # Restart and do renCv
                            print "Turning on doRenCv"
                            self.setVal("doRenCv", 1)
                            print "Returning to", self.parmDic("frStart")
                            fr = self.parmDic("frStart")
                        else:
                            # Stop
                            if self.record:
                                self.recButCmd()
                            fr -= 1
                            self.setVal("anim", 0)
                    # This forces each frame to process.  TODO: maybe add forceFps
                    self.setFrAndUpdate(fr)

                    # For ofs anim.
                    #ofs = fr/float(frPerCycle) % 1
                    ofs = self.getOfs() % 1
                self.setVal("fr", fr)
            Tk.update_idletasks(self.root)
            Tk.update(self.root)

warpUi()
