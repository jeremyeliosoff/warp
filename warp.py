#!/usr/bin/python
import os, genData, utils
from Tkinter import *
import Tkinter
import PIL
from PIL import ImageTk, Image
from tkColorChooser import askcolor              

parmPath = utils.projDir + "/parms"


class showWin():
    def rebuildUI(self):
        print "reloading........"
        self.refreshParms()
        utils.exeCmd("killall warp.py; /home/jeremy/dev/warp/warp.py")
        
    def refreshParms(self):
        print "parmDic", self.parmDic
        for k,v in self.parmDic.parmDic.items():
            thisDic = self.parmDic.parmDic[k]
            #print "\nIN refreshParms: k", k, "thisDic", thisDic
            # Below is just so parmCallback doesn't make errors before all the
            # ui is built - a bit unsatisfying.
            if "uiElement" in thisDic.keys() and not thisDic["type"] == "clr":
                thisDic["val"] = thisDic["uiElement"].get()
        self.saveParmDic()

    def parmCallback(self, sv):
        self.refreshParms()

    def btn_getColor(self, args):
        k,c = args
        print "ZZZZZZZZZZZ in btn_getColor-- k:", k, ", c:", c
        #c = self.parmDic[k]
        c = self.parmDic(k)
        hx = utils.rgb_to_hex(c[0], c[1], c[2])
        print "c:", c
        print "hx:", hx
        color = askcolor(color=hx) 
        print "color", color
        if color:
            clrInt = color[0]
            clrDec = utils.rgb_int_to_dec(clrInt[0], clrInt[1], clrInt[2])
            print "clrDec", clrDec
            self.setVal(k, clrDec)
            postC = self.parmDic(k)
            print "postC", postC
            self.parmDic.parmDic[k]["uiElement"].configure(bg=color[1])
            #self.parmDic[k] = list(clrDec)
            #self.entDic[k].configure(bg=color[1])
            #self.saveParmDic()
    
    def makeParmUi(self, startRow):
        row = startRow
        for k,v in self.parmDic.parmLs: #TODO why k,v?? What's v used for
            thisParmDic = self.parmDic.parmDic[k]
            #print "-------------IN makeParmUi, k:", k, ", thisParmDic:", thisParmDic
            
            if "hidden" in thisParmDic.keys() and thisParmDic["hidden"] == "True":
                print "HIDDEN, skipping..."
                continue
            lab = Label(self.frameParm, text=k)
            lab.grid(row=row, column=0)


            if thisParmDic["type"] == "clr":
                clrTuple = self.parmDic(k)
                print "XXXXXXXXXXX clrTuple", clrTuple
                hx = utils.rgb_to_hex(clrTuple[0],clrTuple[1],clrTuple[2]) #TODO: I think you can directly use floats somehow.
                ent = Button(self.frameParm, width=10, bg=hx,command=lambda args=(k,clrTuple): self.btn_getColor(args))
            else:
                ent = Entry(self.frameParm)
            ent.grid(row=row, column=1)
            thisParmDic["uiElement"] = ent
            print "-------- ent:", ent

            if not thisParmDic["type"] == "clr":
                sv = StringVar()
                sv.trace("w", lambda name, index, mode, sv=sv: self.parmCallback(sv))

                thisParmDic["uiElement"].configure(textvariable=sv)
                thisParmDic["uiElement"].insert(0, str(thisParmDic["val"]))

            row += 1
        self.frameParm.grid(row=0, column=0, sticky=N)
        return row
        

    def positionWindow(self):
        w = 800 # width for the Tk root
        h = 650 # height for the Tk root

        # get screen width and height
        ws = self.root.winfo_screenwidth() # width of the screen
        hs = self.root.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = ws - (w/2)
        y = hs - (h/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))


    def loadImages(self):
        for k,thisImgPath in utils.imagePaths.items():
            pImg = ImageTk.PhotoImage(Image.open(thisImgPath))
            if k in self.images.keys():
                self.images[k]["pImg"] = pImg
                self.images[k]["path"] = thisImgPath
            else:
                self.images[k]= {"pImg":pImg, "path":thisImgPath}


    def refreshImages(self):
        for k,thisDic in self.images.items():
            pImg = ImageTk.PhotoImage(Image.open(thisDic["path"]))
            if k in self.images.keys():
                self.images[k]["pImg"] = pImg
            else:
                self.images[k]= {"pImg":pImg}


    def makeImgButton(self, name, frameParent):
        pImg = self.images[name]["pImg"]
	thisButton = Button(frameParent, image=pImg, command=lambda:self.imgButCmd())
	self.images[name]["button"] = thisButton
        return thisButton


    def refreshPictures(self): 
        genData.saveLevelImg(self.parmDic, self.images)

        self.refreshImages()

        for butName,butDic in self.images.items():
            print "butName", butName, "butDic:", butDic
            if "button" in butDic.keys():
                butDic["button"].configure(image=butDic["pImg"])

        if self.parmDic("anim") == 1:
            self.images["anim"]["button"].configure(image=self.pImgPause)
        else:
            self.images["anim"]["button"].configure(image=self.pImgPlay)


    def imgButCmd(self):
        reload(genData)
        self.refreshParms()
        self.refreshPictures()

    def animButCmd(self):
        self.setVal("anim", 1 if self.parmDic("anim") == 0 else 0)
        self.refreshParms()
        self.refreshPictures()


    def saveParmDic(self):
        print "\n\n\n INSIDE saveParmDic"
        with open(parmPath, 'w') as f:
            for k in self.parmDic.parmLs:
                parm = k[0]
                f.write(parm + "\n")
                thisDic = self.parmDic.parmDic[parm]
                print "k", k, "thisDic", thisDic
                keys = thisDic.keys()
                keys.sort()
                for attr in keys:
                    if not attr == "uiElement":
                        f.write(attr + " " + str(thisDic[attr]) + "\n")
                f.write("\n")


    def getImg(self, selection):
        print " selection",  selection
        self.parmDic.parmDic["image"]["val"] = selection
        self.images["orig"]["path"] = utils.imgTest + "/" + selection
        self.refreshParms()
        print "\n\n------- self.images", self.images
	self.refreshPictures()

    def setVal(self, parmStr, val):
        if "uiElement" in self.parmDic.parmDic[parmStr]:
            uiElement = self.parmDic.parmDic[parmStr]["uiElement"]
            if not self.parmDic.parmDic[parmStr]["type"] == "clr":
                uiElement.delete(0, END)
                uiElement.insert(0, str(val))
        valStr = str(val)
        print "valStr pre", valStr
        if type(val) in [type(()), type([])]:
            valStr = valStr[1:-1].replace(' ','')
        print "valStr pos", valStr
        self.parmDic.parmDic[parmStr]["val"] = valStr
        self.refreshParms()

    def __init__(self):
        self.parmDic = utils.parmDic(parmPath)
        print "\n\n\n********** parmDic2"
        print self.parmDic
        self.root = Tk()
        self.positionWindow()

        sourceImages = os.listdir(utils.imgTest)
        sourceImages.sort()

        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.pImgPlay = ImageTk.PhotoImage(Image.open(utils.imgPlay))
        self.pImgPause = ImageTk.PhotoImage(Image.open(utils.imgPause))

        self.images = {}
        self.loadImages()
        #self.images["orig"]["path"] = utils.imgTest + "/" + self.parmDic.parmDic["image"]["val"]

        self.frameMaster = Frame(self.root)
        self.frameMaster.place(x=1000, y=1000)
	self.frameMaster.grid()

        self.frameParm = Frame(self.frameMaster)
        #self.frameParm.pack(fill=BOTH)
        row = 0

        # Recreate UI button
	self.but_rebuildUi = Button(self.frameParm, text="Recreate UI", command=lambda:self.rebuildUI())
	self.but_rebuildUi.grid(row=row, column=0)
        row +=1

        # Make parm UI


        row = self.makeParmUi(row)

	self.imgLabel = Label(self.frameParm, text="image")
        self.imgLabel.grid(row=row)

        vv = StringVar(self.frameParm)
        vv.set(self.parmDic.parmDic["image"]["val"])
        self.imgChooser = OptionMenu(self.frameParm, vv, *sourceImages, command=self.getImg)
        self.imgChooser.grid(row=row, column=1)
        row += 1

        # Anim button
        thisButton = self.makeImgButton("anim", self.frameParm)
	thisButton.configure(command=lambda:self.animButCmd())
        if self.parmDic("anim") == 1:
            thisButton.configure(image=self.pImgPause)
        else:
            thisButton.configure(image=self.pImgPlay)
        thisButton.grid(row=row)

        # Make picture (button) UI
        self.frameImg = Frame(self.frameMaster)
        self.frameImg.grid(row=0, column=1)
        row = 0
        thisButton = self.makeImgButton("orig", self.frameImg)
        thisButton.grid(row=row)


        thisButton = self.makeImgButton("levels", self.frameImg)
        thisButton.grid(row=row, column=1)
        row +=1

        thisButton = self.makeImgButton("jtGrid", self.frameImg)
        thisButton.grid(row=row)

        thisButton = self.makeImgButton("curves", self.frameImg)
        thisButton.grid(row=row, column=1)
        row +=1


        self.getImg(self.parmDic("image")) # Update main image to reflect current selection.
        #mainloop() 
        count = 0
        while True:
            count += 1
            anim = self.parmDic("anim")
            if anim == 1:
                val = self.parmDic("animIter")
                self.setVal("animIter", val + self.parmDic("animIncr"))

                # For ofs anim.
                k = 1000
                self.setVal("ofs", (self.parmDic("animIter") % k)/float(k))

                self.refreshPictures()
            Tk.update_idletasks(self.root)
            Tk.update(self.root)

showWin()
