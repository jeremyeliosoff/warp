#!/usr/bin/python
import os, genData, utils
from Tkinter import *
import PIL
from PIL import ImageTk, Image
from tkColorChooser import askcolor              

GprojPath = "/home/jeremy/dev/warp/"
GimgPath = GprojPath + "img/single/testAndP.jpg"
GparmPath = GprojPath + "parms"

def jTest():
    print "yes"
    print "__name__", __name__


if __name__ == "__main__":
    print "in main"

print "free statement in warp.py"


#GimgPath = "/home/jeremy/dev/mnc/snapshots/005/img.gif"



class showWin():
    def rebuildUI(self):
        print "reloading........"
        self.refreshParms()
        utils.exeCmd("killall warp.py; /home/jeremy/dev/warp/warp.py")
        
    def refreshParms(self):
        for k,v in self.parmDic.items():
            thisDic = self.parmDic[k]
            thisDic["val"] = thisDic["uiElement"].get()
        self.saveParmDic()


    def parmLsToDic(self, ls):
        parmDic = {}
        for k,v in ls:
            print "k", k
            print "v", v
            print
            parmDic[k] = v

        return parmDic

    def makeParmUi(self, startRow):
        row = startRow
        for k,v in self.parmLs:
            thisParmDic = self.parmDic[k]
            print "in makeParmUi, thisParmDic:", thisParmDic
            
            lab = Label(self.frameParm, text=k)
            lab.grid(row=row, column=0)

            ent = Entry(self.frameParm)
            ent.insert(0, str(thisParmDic["val"]))
            ent.grid(row=row, column=1)
            thisParmDic["uiElement"] = ent

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
        #x = (ws/2) - (w/2)
        #y = (hs/2) - (h/2)
        x = ws - (w/2)
        y = hs - (h/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def getParmVal(self, parm):
        thisParmDic = self.parmDic[parm]
        strVal = thisParmDic["val"]
        typ = thisParmDic["type"]
        if typ == "int":
            return int(strVal)
        elif typ == "float":
            return float(strVal)
        else:
            return strVal
        


    def imgButCmd(self):
        reload(genData)
        self.refreshParms()
        imgPath, imgPathOut = genData.saveLevelImg(self.getParmVal("nLevels"))
        self.photo = ImageTk.PhotoImage(Image.open(imgPath))
        self.photo2 = ImageTk.PhotoImage(Image.open(imgPathOut))
	self.imgBut.configure(image=self.photo)
	self.imgBut2.configure(image=self.photo2)

    def saveParmDic(self):
        print "\n\n\n"
        print "\n\n\n INSIDE saveParmDic"
        with open(GparmPath, 'w') as f:
            for k in self.parmLs:
                parm = k[0]
                f.write(parm + "\n")
                thisDic = self.parmDic[parm]
                print "thisDic", thisDic
                keys = thisDic.keys()
                keys.sort()
                for attr in keys:
                    if not attr == "uiElement":
                        f.write(attr + " " + str(thisDic[attr]) + "\n")
                f.write("\n")



    def loadParmLs(self):
        print "\n\n\n"
        print "\n\n\n INSIDE loadParmLs"
        parmLs = []
        thisParmDic = {}
        thisParmName = ""
        nextIsParm = True
        with open(GparmPath) as f:
            for line in f.readlines():
                stripped = line.strip()
                if stripped == "":
                    nextIsParm = True
                else:
                    if nextIsParm:
                        if not thisParmName == "":
                            parmLs.append([thisParmName, thisParmDic])
                        thisParmName = stripped
                        thisParmDic = {}
                    else:
                        k,v = stripped.split()
                        thisParmDic[k] = v
                        
                    nextIsParm = False
                #print "-----------"
                print "line:", line
                #print "stripped:", stripped
                #print "nextIsParm:", nextIsParm

        parmLs.append([thisParmName, thisParmDic])
        print "\n\n\n"
        print parmLs
        return parmLs






    def __init__(self):
        self.parmLs = self.loadParmLs()[:]
        print "================== parmLs", self.parmLs
        self.parmDic = self.parmLsToDic(self.parmLs)
        print "================== parmDic", self.parmDic
        self.root = Tk()
        self.positionWindow()


        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.photo = ImageTk.PhotoImage(Image.open(GimgPath))
        self.photo2 = ImageTk.PhotoImage(Image.open(genData.imgPathOut))
        #self.photo2 = PhotoImage(file=GimgPath)

        self.frameMaster = Frame(self.root)
        self.frameMaster.place(x=1000, y=1000)
	self.frameMaster.grid()

        self.frameParm = Frame(self.frameMaster)
        #self.frameParm.pack(fill=BOTH)
        row = 0
	self.but_rebuildUi = Button(self.frameParm, text="Recreate UI", command=lambda:self.rebuildUI())
	self.but_rebuildUi.grid(row=row, column=0)
        row +=1

        #self.parmLs = self.loadParmLs()
        print "vvvvvv self.parmDic", self.parmDic
        row = self.makeParmUi(row)

        self.frameImg = Frame(self.frameMaster)
        self.frameImg.grid(row=0, column=1)
        row = 0
	self.imgBut = Button(self.frameImg, image=self.photo, command=lambda:self.imgButCmd())
        self.imgBut.grid(row=row)
        row +=1


	self.imgBut2 = Button(self.frameImg, image=self.photo2, command=lambda:self.imgButCmd())
        self.imgBut2.grid(row=row)
	#frameParm = Frame(self.frameControls)
        mainloop() 

showWin()
