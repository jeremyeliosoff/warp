#!/usr/bin/python

#from tkColorChooser import askcolor              
import os, ut, copy, math, pygame
from Tkinter import *
import numpy as np
from PIL import ImageTk, Image

warpDir = "/home/jeremy/dev/warp"
renDir = warpDir + "/ren"
renDirKscope = renDir + "/kScope"
parmFile = warpDir + "/kScopeParms"
parmDefFile = warpDir + "/kScopeParmsDef"
errorImgPath = ut.imgDir + "/controls/error.png"
displayHt = 480


class kWin():

	# Hotkeys
	def frChange(self, inc):
		fr = ut.clamp(self.parmVal("fr") + inc, self.frStart, self.frEnd)
		print "_frChange(): fr =", fr
		self.strValToParmDic("fr", fr)
		var = self.parmDic["fr"]["ui"]["var"]
		var.set(str(fr))
		self.saveUIToParmsAndFile("fr", var)
		self.updateImages()

	def ctlReturnCmd(self):
		focused = self.frameMaster.focus_get()
		print "_returnCmd(): focused:", focused
		#print "_returnCmd(): self.verUI[ren][sfx]:", self.verUI["ren"]["sfx"]
		if focused == self.nextRenVerEntry:
			print "_returnCmd(): \tIT'S NEXTVER!!!!!!!!"
			#self.butVNew("ren")
			vers = ut.getVersions(renDirKscope)
			nextVerInt = int(vers[0][1:4]) + 1
			nextVerSfx = self.nextRenVerEntry.get()
			nextVer = ("v%03d" % nextVerInt) + nextVerSfx
			nextVerPath = renDirKscope + "/" + nextVer
			print "\n_ctlReturnCmd(): making", nextVerPath
			ut.mkDirSafe(nextVerPath)
		else:
			print "NOTHIN!!!"
		

	# Other
	def parmVal(self, parmName):
		return self.parmDic[parmName]["val"]
	
	def scaleToDisplayHt(self, img):
		res = img.size
		ratio = float(displayHt)/res[1]
		return img.resize((int(res[0]*ratio), int(res[1]*ratio)))


	def updateImages(self):
		print "_updateImages(): BEGIN"
		ff = "%05d" % self.parmVal("fr")
		self.inImgPath = warpDir + "/ren/" + self.parmVal("image0") + "/" + \
			self.parmVal("version0") + "/ren/ALL/ren.ALL." + ff + ".png"
		loadedImg = Image.open(self.inImgPath)
		#res = loadedImg.size
		loadedImg = self.scaleToDisplayHt(loadedImg)
		self.inPhoto = ImageTk.PhotoImage(loadedImg)
		self.inImgBut.configure(image=self.inPhoto)
		self.outImgPath = warpDir + "/ren/testImg/testImg." + ff + ".png"
		renVer = self.parmVal("renVer")
		self.outImgPath = renDirKscope + "/" + renVer + "/" + renVer + "." + ff + ".png"
		if os.path.exists(self.outImgPath):
			loadedImg = Image.open(self.outImgPath)
		else:
			loadedImg = Image.open(errorImgPath)
		loadedImg = self.scaleToDisplayHt(loadedImg)
		self.outPhoto = ImageTk.PhotoImage(loadedImg)
		#self.outPhoto.resize(100,100)
		self.outImgBut.configure(image=self.outPhoto)
		print "_updateImages(): set self.inImgPath =", self.inImgPath
		print "_updateImages(): set self.outImgPath =", self.outImgPath

	def processImgSeq(self):
		for fr in range(self.frStart, self.frEnd):
			self.strValToParmDic("fr", fr)
			print "Rendering", self.outImgPath
			self.processImg()

	def loadImgNum(self, num):
		ff = "%05d" % self.parmVal("fr")
		imgPath = warpDir + "/ren/" + self.parmVal("image" + str(num)) + "/" + \
			self.parmVal("version" + str(num)) + "/ren/ALL/ren.ALL." + ff + ".png"
		return pygame.image.load(imgPath)
		
	def processImg(self):
		self.updateImages()
		im = pygame.image.load(self.inImgPath)
		sz = im.get_size()
		#im = Image.open(self.inImgPath)
		imAr = pygame.surfarray.pixels3d(im)
		#print "imArF", imArF
		#print "im", im
		imArF = imAr.astype(np.float32)

		#imOutF = imArF.astype('float')
		imArOutF = np.zeros(imArF.shape, dtype=np.float)
		imOut = im.copy()
		imOut.fill(0)
		imBlank = imOut.copy()

		nRots = 4
		fr = self.parmVal("fr")
		prog = ut.fit(fr, self.frStart, self.frEnd, 0, 1)

		for imgNum in range(2):
			sc = ut.mix(self.parmVal("scB" + str(imgNum)), self.parmVal("scE" + str(imgNum)), prog)
			tx = ut.mix(self.parmVal("txB" + str(imgNum)), self.parmVal("txE" + str(imgNum)), prog)
			ty = ut.mix(self.parmVal("tyB" + str(imgNum)), self.parmVal("tyE" + str(imgNum)), prog)
			print "_processImg(): prog=", ("%05.4f" % prog), "sc=", sc, "tx=", tx, "ty=", ty
			im = self.loadImgNum(imgNum)
			sz = im.get_size()
			for i in range(nRots):
				imMod = imBlank.copy()
				imCp = im.copy()
				imCp = pygame.transform.scale(imCp, (int(sz[0]*sc), int(sz[1]*sc)))

				txAbs = tx * sz[0]
				tyAbs = ty * sz[1]
				txRem = txAbs % 1
				tyRem = tyAbs % 1
				#print "\n----tx", tx
				#print "----ty", ty
				for txInt, txMult in ((math.floor(txAbs), 1-txRem), (math.floor(txAbs)+1, txRem)):
					for tyInt, tyMult in ((math.floor(tyAbs), 1-tyRem), (math.floor(tyAbs)+1, tyRem)):
						thisImCp = imCp.copy()
						k = txMult * tyMult
						#print "----------txInt", txInt
						#print "----------tyInt", tyInt
						#print "----------txMult", txMult
						#print "----------tyMult", tyMult
						#print "----------k", k

						thisImCp.fill((255*k, 255*k, 255*k), None, pygame.BLEND_MULT)
						imMod.blit(thisImCp, (txInt, tyInt), (0, 0, sz[0], sz[1]), pygame.BLEND_ADD)

				imCpSzOld = imMod.get_size()
				imMod = pygame.transform.rotate(imMod, (i+(.5*(imgNum % 2)) + .002*fr)*360.0/nRots)
				#imMod = pygame.transform.rotate(imMod, i*45)
				imCpSzNew = imMod.get_size()
				xStart = imCpSzOld[0] - imCpSzNew[0]
				yStart = imCpSzOld[1] - imCpSzNew[1]
				imOut.blit(imMod, (0, 0), (-xStart/2, -yStart/2, sz[0], sz[1]), pygame.BLEND_ADD)

		print "_processImg(): saving", self.outImgPath, "..."
		pygame.image.save(imOut, self.outImgPath)
		self.updateImages()
		#im1.save(self.outImgPath)

	def loadParms(self, defaults):
		print "_loadParms(): BEGIN"
		if defaults:
			filePath = parmDefFile
		else:
			filePath = parmFile
		curParm = None
		curType = None
		curVal = None
		if defaults:
			self.parmDic = {}
			self.parmLs = []
		with open(filePath, "r") as f:
			for lnRaw in f.readlines() + ["DUD"]: #DUD to process last parm
				ln = lnRaw.strip()
				print "_loadParms(): ln =", ln
				words = ln.split()
				print "_loadParms(): words =", words
				print "_loadParms(): len(words) =", len(words)
				nWords = len(words)
				if nWords == 1:
					if curParm: # Not None, which would mean this is first parm (no cur parm)
						if defaults:
							if curType == "int":
								self.parmDic[curParm] = {"type":"int", "val":int(curVal)}
							elif curVal == "float":
								self.parmDic[curParm] = {"type":curType, "val":float(curVal)}
							else:
								self.parmDic[curParm] = {"type":curType, "val":curVal}
							self.parmLs.append(curParm)
						elif curParm in self.parmDic.keys(): # Only assign if in defaults
							thisType = self.parmDic[curParm]["type"]
							self.strValToParmDic(curParm, curVal)
							#if thisType == "int":
							#	self.parmDic[curParm]["val"] = int(curVal)
							#else:
							#	self.parmDic[curParm]["val"] = float(curVal)
					curParm = words[0]
				elif nWords == 2:
					if words[0] == "type":
						curType = words[1]
					else:
						curVal = words[1]
		print "_loadParms(): self.parmDic =", self.parmDic


	def strValToParmDic(self, parmName, val):
		if parmName in self.parmDic.keys():
			typ = self.parmDic[parmName]["type"]
			if typ == "int":
				self.parmDic[parmName]["val"] = int(val)
			elif typ == "float":
				print "---------- val", val
				self.parmDic[parmName]["val"] = float(val)
			else:
				self.parmDic[parmName]["val"] = val
				
	def saveUIToParmsAndFile(self, pn, sv):
		val = sv.get()
		self.strValToParmDic(pn, val)
		print "_saveUIToParmsAndFile(): pn", pn, "sv", sv, "val", val
		with open(parmFile, "w") as f:
			for parmName in self.parmLs:
				parmVal = self.parmDic[parmName]["val"]
				f.write(parmName + "\n")
				f.write("value " + str(parmVal) + "\n\n")
			

	def menuImgChooser(self, selection, numStr):
		print "_menuImgChooser(): self.imgChooserVar.get()", self.imgChooserVar.get(), "selection", selection, "numStr", numStr
		versDir = renDir + "/" + selection
		vers = os.listdir(versDir)
		vers.sort()
		verLatest = vers[-1]
		print "_menuImgChooser(): verLatest=", verLatest
		self.verChooserVar.set(verLatest)
		self.strValToParmDic("image" + numStr, selection)
		self.strValToParmDic("version" + numStr, verLatest)
		self.updateImages()

	def menuVerChooser(self, selection):
		print "_menuImgChooser(): self.verChooserVar.get()", self.verChooserVar.get(), "selection", selection

	def menuRenVerChooser(self, selection):
		print "_menuRenImgChooser(): self.renDirVar.get()", self.renDirVar.get(), "selection", selection
		#self.strValToParmDic("renVer", selection)
		self.saveUIToParmsAndFile("renVer", self.renDirVar)
		self.updateImages()

	def makeParmLabelEntry(self, parmName, row):
		parmVal = self.parmDic[parmName]["val"]
		label = Label(self.frameCtls, width=10, text=parmName)
		label.grid(row=row)

		entry = Entry(self.frameCtls, width=10)
		entry.insert(0, str(parmVal))
		entry.grid(row=row, column=1)

		var = StringVar()
		var.trace("w", lambda name, index, mode, sv=var,
			pn=parmName: self.saveUIToParmsAndFile(pn, sv))

		entry.configure(textvariable=var)
		entry.insert(0, str(parmVal))

		self.parmDic[parmName]["ui"] = {
			"label": label,
			"entry": entry,
			"var": var,
			}


	def __init__(self):
		#frStill = 2137
		#for fr in range(frStill, frStill+1):
		self.frStart = 1753
		self.frEnd = 2300

		self.root = Tk()
		self.root.bind('<Escape>', lambda e: self.root.destroy())

		self.frameMaster = Frame(self.root)
		self.frameMaster.grid()

		self.frameCtls = Frame(self.frameMaster)
		self.frameCtls.grid(row=0,column=0)

		self.frameImgs = Frame(self.frameMaster)
		self.frameImgs.grid(row=0,column=1)

		# Load parms
		self.loadParms(True)
		self.loadParms(False)

		# Controls
		row = 0

		nClips = 2
		BEParms = ["tx", "ty", "sc"]

		self.renderedClips = os.listdir(ut.renDir)
		self.renderedClips.sort()

		self.makeParmLabelEntry("fr", row)
		row += 1

		for clipNum in range(nClips):

			# Menus
			for menuParm in ["image", "version"]:
				imgParmName = menuParm + str(clipNum)
				label = Label(self.frameCtls, text=imgParmName)
				label.grid(row=row)

				clipChooserVal = self.parmVal(imgParmName)
				clipChooserVar = StringVar(self.frameCtls)
				clipChooserVar.set(clipChooserVal)
			
				if menuParm == "image":
					selections = self.renderedClips
				else:
					selections = os.listdir(ut.renDir + "/" + self.parmVal("image0"))
					selections.sort()
				clipChooser = OptionMenu(self.frameCtls, clipChooserVar, *selections,
							command=lambda selection, numStr=str(clipNum) : self.menuImgChooser(selection, numStr))
				clipChooser.grid(row=row, column=1)
				
				row +=1

				self.parmDic[imgParmName]["ui"] = {
					"label": label,
					"var": clipChooserVar,
					}

			# Parms like txB0, txE0, tyB0....
			for BEParm in BEParms:
				for BE in "BE":
					parmName = BEParm + BE + str(clipNum)
					self.makeParmLabelEntry(parmName, row)
					row += 1


		self.renDirVar = StringVar()
		self.renDirVar.set(self.parmVal("renVer"))
		self.renDirVar.trace("w", lambda name, index, mode, sv=self.renDirVar,
			pn="renVerOut": self.saveUIToParmsAndFile(pn, sv))


		renVersions = os.listdir(ut.renDir + "/kScope")
		self.renDirVerChooser = OptionMenu(self.frameCtls, self.renDirVar, *renVersions, command=self.menuRenVerChooser)
		self.renDirVerChooser.grid(row=row)

		self.nextRenVerEntry = Entry(self.frameCtls, width=10)
		self.nextRenVerEntry.grid(row=row, column=1)
		row += 1

		# Images
		self.inImgBut = Button(self.frameImgs)
		self.inImgBut.grid(row=0)
		self.outImgBut = Button(self.frameImgs)
		self.updateImages()
		self.outImgBut.grid(row=1)
		
		# Key bindings
		self.root.bind('<Alt-Return>', lambda e: self.processImg())
		self.root.bind('<Control-Alt-Return>', lambda e: self.processImgSeq())
		self.root.bind('<Control-Return>', lambda e: self.ctlReturnCmd())
		self.root.bind('<Right>', lambda e: self.frChange(1))
		self.root.bind('<Left>', lambda e: self.frChange(-1))
		self.root.bind('<Shift-Right>', lambda e: self.frChange(10))
		self.root.bind('<Shift-Left>', lambda e: self.frChange(-10))
		self.root.bind('<Control-Right>', lambda e: self.frChange(100000))
		self.root.bind('<Control-Left>', lambda e: self.frChange(-100000))

		mainloop() 

kWin()
