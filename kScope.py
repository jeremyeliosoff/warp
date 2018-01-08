#!/usr/bin/python

#from tkColorChooser import askcolor              
import os, ut, copy, math, pygame
from Tkinter import *
import numpy as np
from PIL import ImageTk, Image

warpDir = "/home/jeremy/dev/warp"
renDir = warpDir + "/ren"
parmFile = warpDir + "/kScopeParms"
parmDefFile = warpDir + "/kScopeParmsDef"


class kWin():
	# Hotkeys
	def frChange(self, inc):
		fr = ut.clamp(self.parmVal("fr") + inc, self.frStart, self.frEnd)
		print "_rightCmd(): fr =", fr
		self.strValToParmDic("fr", fr)
		var = self.parmDic["fr"]["ui"]["var"]
		var.set(str(fr))
		self.saveUIToParmsAndFile("fr", var)
		self.updateImages()
		

	def parmVal(self, parmName):
		return self.parmDic[parmName]["val"]

	def updateImages(self):
		print "_updateImages(): BEGIN"
		ff = "%05d" % self.parmVal("fr")
		self.inImgPath = warpDir + "/ren/" + self.parmVal("image0") + "/" + \
			self.parmVal("version0") + "/ren/ALL/ren.ALL." + ff + ".png"
		self.inPhoto = PhotoImage(file=self.inImgPath);
		self.inImgBut.configure(image=self.inPhoto)
		self.outImgPath = warpDir + "/ren/testImg/testImg." + ff + ".png"
		if os.path.exists(self.outImgPath):
			self.outPhoto = PhotoImage(file=self.outImgPath);
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
			

	def menuImgChooser(self, selection, num):
		print "_menuImgChooser(): self.imgChooserVar.get()", self.imgChooserVar.get(), "selection", selection, "num", num
		versDir = renDir + "/" + selection
		vers = os.listdir(versDir)
		vers.sort()
		verLatest = vers[-1]
		print "_menuImgChooser(): verLatest=", verLatest
		self.verChooserVar.set(verLatest)
		self.strValToParmDic("image" + num, selection)
		self.strValToParmDic("version" + num, verLatest)
		self.updateImages()

	def menuVerChooser(self, selection):
		print "_menuImgChooser(): self.verChooserVar.get()", self.verChooserVar.get(), "selection", selection

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
		#for parmName,parmAtts in self.parmDic.items():

		# Src Images	
		#for i in range(2):
		#	sourceSequences = os.listdir(ut.renDir)
		#	sourceSequences.sort()
		#	self.imgChooserVar = StringVar(self.frameCtls)
		#	self.imgChooserVar.set(self.parmVal("image" + str(i)))
		#	self.imgChooser = OptionMenu(self.frameCtls, self.imgChooserVar, *sourceSequences,
		#		command=lambda selection, num=i : self.menuImgChooser(selection, num))
		#	label = Label(self.frameCtls, text="image" + str(i))
		#	label.grid(row=row, column=0)
		#	self.imgChooser.grid(row=row, column=1)
		#	row += 1

		#	sourceSequences = os.listdir(ut.renDir + "/" + self.parmVal("image0"))
		#	sourceSequences.sort()
		#	self.verChooserVar = StringVar(self.frameCtls)
		#	self.verChooserVar.set(self.parmVal("version" + str(i)))
		#	self.verChooser = OptionMenu(self.frameCtls, self.verChooserVar, *sourceSequences, command=self.menuVerChooser)
		#	label = Label(self.frameCtls, text="version" + str(i))
		#	label.grid(row=row, column=0)
		#	self.verChooser.grid(row=row, column=1)
		#	row += 1

		for parmName in self.parmLs:
			if parmName[:-1] in ["image", "version"]:
				imgNum = parmName[-1]
				if parmName[:-1] == "image":
					sourceSequences = os.listdir(ut.renDir)
					sourceSequences.sort()
					self.imgChooserVar = StringVar(self.frameCtls)
					self.imgChooserVar.set(self.parmVal("image" + imgNum))
					self.imgChooser = OptionMenu(self.frameCtls, self.imgChooserVar, *sourceSequences,
						command=lambda selection, num=imgNum : self.menuImgChooser(selection, num))
					label = Label(self.frameCtls, text="image" + imgNum)
					label.grid(row=row, column=0)
					self.imgChooser.grid(row=row, column=1)
					row += 1

				else:
					sourceSequences = os.listdir(ut.renDir + "/" + self.parmVal("image0"))
					sourceSequences.sort()
					self.verChooserVar = StringVar(self.frameCtls)
					self.verChooserVar.set(self.parmVal("version" + imgNum))
					self.verChooser = OptionMenu(self.frameCtls, self.verChooserVar, *sourceSequences, command=self.menuVerChooser)
					label = Label(self.frameCtls, text="version" + imgNum)
					label.grid(row=row, column=0)
					self.verChooser.grid(row=row, column=1)
					row += 1
				continue
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
			row += 1

		# Images
		ff = "%05d" % self.parmVal("fr")
		self.inImgPath = warpDir + "/ren/" + self.parmVal("image0") + "/" + \
			self.parmVal("version0") + "/ren/ALL/ren.ALL." + ff + ".png"
		self.outImgPath = warpDir + "/ren/testImg/testImg." + ff + ".png"
		self.inPhoto = PhotoImage(file=self.inImgPath);
		self.inImgBut = Button(self.frameImgs, image=self.inPhoto)
		self.inImgBut.grid(row=0)
		self.outImgBut = Button(self.frameImgs)
		if os.path.exists(self.outImgPath):
			self.outPhoto = PhotoImage(file=self.outImgPath);
			self.outImgBut.configure(image=self.outPhoto)
		self.outImgBut.grid(row=1)
		
		# Key bindings
		self.root.bind('<Alt-Return>', lambda e: self.processImg())
		self.root.bind('<Control-Return>', lambda e: self.processImgSeq())
		self.root.bind('<Right>', lambda e: self.frChange(1))
		self.root.bind('<Left>', lambda e: self.frChange(-1))
		self.root.bind('<Shift-Right>', lambda e: self.frChange(10))
		self.root.bind('<Shift-Left>', lambda e: self.frChange(-10))
		self.root.bind('<Control-Right>', lambda e: self.frChange(100000))
		self.root.bind('<Control-Left>', lambda e: self.frChange(-100000))

		mainloop() 

kWin()
