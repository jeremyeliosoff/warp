#!/usr/bin/python

#from tkColorChooser import askcolor              
import os, ut, copy, math, pygame, shutil
from Tkinter import *
import numpy as np
from PIL import ImageTk, Image

warpDir = "/home/jeremy/dev/warp"
renDir = warpDir + "/ren"
renDirKscope = renDir + "/kScope"
parmFile = warpDir + "/kScopeParms"
parmDefFile = warpDir + "/kScopeParmsDef"
errorImgPath = ut.imgDir + "/controls/error.png"
displayHt = 200

clipDic = {
	#"newArrBUQ_GOODHR_vig":{"range":(600,2500)},
	"sub_comingHR_vig":{"range":(1650,2325)},
	#"sub_coming_vig":{"range":(1750,2300)},
	"newArrBUQ_GOODHR_vig":{"range":(425,1050)},
	"sub_comingPplHR_vig":{"range":(3800,4399)},
	"newArrBUQ_PplHR_vig":{"range":(925,1550)},
	"sub_goingHR_vig":{"range":(1,1245)},
	#"sub_goingHR_vig_cp":{"range":(1750,2300)},
	"newDepMtRDarkHR_vig":{"range":(1,750)},
}

resOptions = (
	"480x270",
	"960x540",
	"1920x1080")

#resOptions = (
#	(480, 270),
#	(960, 540),
#	(1920, 1080))

for clip,dic in clipDic.items():
	rg = dic["range"]
	dic["len"] = rg[1]-rg[0]+1
	

class kWin():
	def makeClipSeq(self):
		self.clipSeq = []
		for clipNum in range(self.nClips):
			self.clipSeq.append(self.parmVal("image" + str(clipNum)))
		print "\n\n_makeClipSeq(): self.clipSeq=", self.clipSeq

	def makeClipFrOfs(self):
		self.clipSeqOfs = []
		for clipNum in range(len(self.clipSeq)):
			clip = self.clipSeq[clipNum]
			rg = clipDic[clip]["range"]
			ln = clipDic[clip]["len"]
			offset = rg[0]
			if clipNum == 0:
				total = ln
			else:
				# This is a bit tricky: 
				if ln < prevLn:
					total += ln/2
				else:
					total += ln - prevLn/2
				offset += -(total - ln)
			self.clipSeqOfs.append(offset)
			prevLn = ln
			print "\n\n_makeClipFrOfs(): clipNum=", clipNum, ", clip=", clip, ", total=", total, ", offset=", offset
		self.frRange = total
	
	def getActiveClipNums(self):
		activeClipNums = []
		fr = self.parmVal("fr")
		for clipNum in range(self.nClips):
			ofs = self.clipSeqOfs[clipNum]
			frWOfs = fr+ofs
			clip = self.clipSeq[clipNum]
			print "clipNum=", clipNum, ", clip=", clip, ", ofs", ofs, ", fr=", fr, ", frWOfs=", frWOfs
			rg = clipDic[clip]["range"]
			if frWOfs >= rg[0] and frWOfs <= rg[1]:
				activeClipNums.append(clipNum)
		return activeClipNums

	def getClipFr(self, clipNum):
		fr = self.parmVal("fr")
		ofs = self.clipSeqOfs[clipNum]
		return fr + ofs

	# Hotkeys
	def hkEsc(self):
		focused = self.frameMaster.focus_get()
		if focused == self.frameMaster:
			self.root.destroy()
		else:
			self.frameMaster.focus_set()

		
		self.root.bind('<Escape>', lambda e: self.root.destroy())


	def valNudge(self, inc, doRen=False):
		focused = self.frameMaster.focus_get()
		parmName = self.entryDic[focused]
		print "_valNudge(): parmName=", parmName, "inc=", inc, "doRen=", doRen
		curVal = self.parmVal(parmName)
		#self.strValToParmDic(parmName, curVal + inc)
		self.parmDic[parmName]["ui"]["var"].set(curVal + inc)
		
		if doRen:
			self.processImg()


	def setClipHighlight(self):
		print "_setClipHighlight(): BEGIN"
		fr = self.parmVal("fr")
		for clipNum in range(self.nClips):
			seqRng = self.clipRngAndSeqRng(clipNum)[1]
			if fr >= seqRng[0] and fr <= seqRng[1]:
				self.outImgButs[clipNum].configure(highlightbackground="red")
			else:
				self.outImgButs[clipNum].configure(highlightbackground="black")


	def frChange(self, inc):
		focused = self.frameMaster.focus_get()
		#print "\n --------- focused", focused, "\n"
		#print "self.entryDic.keys()", self.entryDic.keys()
		if focused in self.entryDic.keys():
			print "_frChange(): not changing, focus on an entry."
		else:
			fr = ut.clamp(self.parmVal("fr") + inc, 0, self.frRange)
			#fr = self.parmVal("fr") + inc
			print "_frChange(): fr =", fr
			self.strValToParmDic("fr", fr)
			var = self.parmDic["fr"]["ui"]["var"]
			var.set(str(fr))
			self.saveUIToParmsAndFile("fr", var)
			self.updateOutImg()
			activeClipNums = self.getActiveClipNums()
			print "_frChange(): self.clipSeq:"
			for clipNum in range(len(self.clipSeq)):
				clip = self.clipSeq[clipNum]
				#print "\t", clipNum, ":", clip, "range", clipDic[clip]["range"], "len", clipDic[clip]["len"]
			print "_frChange(): activeClipNums:"
			for clipNum in activeClipNums:
				ofs = self.clipSeqOfs[clipNum]
				frWOfs = fr + ofs
				#print "\t", clipNum, ":", self.clipSeq[clipNum], "ofs", ofs, "frWOfs=", frWOfs
			print "_frChange(): END\n"
		self.setClipHighlight()

	def ctlReturnCmd(self):
		focused = self.frameClips.focus_get()
		print "_returnCmd(): focused:", focused
		#print "_returnCmd(): self.verUI[ren][sfx]:", self.verUI["ren"]["sfx"]
		if focused == self.nextRenVerEntry:
			print "_returnCmd(): \tIT'S NEXTVER!!!!!!!!"
			# TODO: can we make this into a function and reuse to init renDirVerChooser?
			vers = ut.getVersions(renDirKscope)
			vers.sort()
			vers.reverse()
			nextVerInt = int(vers[0][1:4]) + 1
			nextVerSfx = self.nextRenVerEntry.get()
			nextVer = ("v%03d" % nextVerInt) + nextVerSfx
			nextVerPath = renDirKscope + "/" + nextVer
			print "\n_ctlReturnCmd(): making", nextVerPath
			ut.mkDirSafe(nextVerPath)
			self.setMenuItems(self.renDirVerChooser["menu"], self.renDirVar, vers, nextVer)
			self.saveUIToParmsAndFile("renVer", self.renDirVar)
		else:
			print "NOTHIN!!!"
		

	# Other
	def parmVal(self, parmName):
		return self.parmDic[parmName]["val"]
	
	def scaleToHt(self, img, ht):
		res = img.size
		ratio = float(ht)/res[1]
		return img.resize((int(res[0]*ratio), int(res[1]*ratio)))

	def safeLoadImg(self, imgPath):
		if os.path.exists(imgPath):
			loadedImg = Image.open(imgPath)
		else:
			loadedImg = Image.open(errorImgPath)
		return loadedImg

	def getOutImgPath(self, fr):
		ff = "%05d" % fr
		renVer = self.parmVal("renVer")
		#self.outImgPath = renDirKscope + "/" + renVer + "/" + renVer + "." + ff + ".png"
		#return self.safeLoadImg(self.outImgPath)
		return renDirKscope + "/" + renVer + "/" + renVer + "." + ff + ".png"
	
	def updateOutImg(self):
		print "_updateImages(): BEGIN"
		fr = self.parmVal("fr")
		#ff = "%05d" % fr
		#self.inImgPath = warpDir + "/ren/" + self.parmVal("image0") + "/" + \
		#	self.parmVal("version0") + "/ren/ALL/ren.ALL." + ff + ".png"
		#self.outImgPath = warpDir + "/ren/testImg/testImg." + ff + ".png"
		#renVer = self.parmVal("renVer")
		#self.outImgPath = renDirKscope + "/" + renVer + "/" + renVer + "." + ff + ".png"
		#loadedImg = self.safeLoadImg(self.outImgPath)
		self.outImgPath = self.getOutImgPath(fr)
		loadedImg = self.safeLoadImg(self.outImgPath)
		loadedImgMain = self.scaleToHt(loadedImg, displayHt*2)
		self.outPhoto = ImageTk.PhotoImage(loadedImgMain)
		#self.outPhoto.resize(100,100)
		self.outImgBut.configure(image=self.outPhoto)

	def updateClipImgs(self):
		self.clipPhotosTmp = []
		for clipNum in range(self.nClips):

			# Get ren mid fr
			#imgDir = self.getImgNumDir(clipNum)
			#renImgs = os.listdir(imgDir)
			#renImgs.sort()
			clip = self.clipSeq[clipNum]
			rg = clipDic[clip]["range"]
			mid = (rg[0] + rg[1])/2
			ofs = self.clipSeqOfs[clipNum]
			outFr = mid-ofs
			#print "\n\n---------_updateClipImgs(): clip", clip, ": rg=", rg, "loading outFr", outFr, "corresponding to clip mid", mid
			print
			loadedImg = self.safeLoadImg(self.getOutImgPath(mid-ofs))

			#print "_updateImages(): BEGIN"
			#ff = "%05d" % self.parmVal("fr")
			#self.inImgPath = warpDir + "/ren/" + self.parmVal("image0") + "/" + \
			#	self.parmVal("version0") + "/ren/ALL/ren.ALL." + ff + ".png"
			#self.outImgPath = warpDir + "/ren/testImg/testImg." + ff + ".png"
			#renVer = self.parmVal("renVer")
			#self.outImgPath = renDirKscope + "/" + renVer + "/" + renVer + "." + ff + ".png"
			#loadedImg = self.safeLoadImg(imgPath)
			loadedImgMain = self.scaleToHt(loadedImg, displayHt*2)
			#self.outPhoto = ImageTk.PhotoImage(loadedImgMain)
			#self.outPhoto.resize(100,100)
			#self.outImgBut.configure(image=self.outPhoto)
			loadedImgClipTmp = self.scaleToHt(loadedImg, displayHt*.55)
			self.clipPhotosTmp.append(ImageTk.PhotoImage(loadedImgClipTmp))
			self.outImgButs[clipNum].configure(image=self.clipPhotosTmp[clipNum])
		print "_updateImages(): set self.outImgPath =", self.outImgPath

	def processImgSeq(self, rng=None):
		#for fr in range(self.frStart, self.frEnd):
		print "_processImgSeq(): BEGIN, rng=", rng
		rngToUse = rng if rng else (0, self.frRange)
		for fr in range(rngToUse[0], rngToUse[1]):
			self.strValToParmDic("fr", fr)
			print "_processImgSeq(): Rendering", self.outImgPath
			self.processImg()


	def getImgNumDir(self, num):
		return warpDir + "/ren/" + self.parmVal("image" + str(num)) + "/" + \
			self.parmVal("version" + str(num)) + "/ren/ALL/"


	def getImgNumPath(self, num, fr):
		if fr == None:
			ff = "%05d" % self.parmVal("fr")
		else:
			ff = "%05d" % fr

		return self.getImgNumDir(num) + "ren.ALL." + ff + ".png"


	def loadImgNum(self, num, fr=None):
		imgPath = self.getImgNumPath(num, fr)
		return pygame.image.load(imgPath)
		
	def processImg(self):
		self.updateOutImg()

		imOut = pygame.Surface(self.res, 24)
		imBlank = imOut.copy()

		nRots = 4
		fr = self.parmVal("fr")

		activeClipNums = self.getActiveClipNums()

		for clipNum in activeClipNums:
			clipFr = self.getClipFr(clipNum)
			clip = self.clipSeq[clipNum]
			rg = clipDic[clip]["range"]
			prog = ut.fit(clipFr, rg[0], rg[1], 0, 1)
			sc = ut.mix(self.parmVal("scB" + str(clipNum)), self.parmVal("scE" + str(clipNum)), prog)
			tx = ut.mix(self.parmVal("txB" + str(clipNum)), self.parmVal("txE" + str(clipNum)), prog)
			ty = ut.mix(self.parmVal("tyB" + str(clipNum)), self.parmVal("tyE" + str(clipNum)), prog)
			print "_processImg(): prog=", ("%05.4f" % prog), "sc=", sc, "tx=", tx, "ty=", ty
			im = self.loadImgNum(clipNum, clipFr)
			res = self.res
			#im = im.resize((int(res[0]), int(res[1])))
			#print "\nPRE------ im.get_size()", im.get_size()
			im = pygame.transform.scale(im, (res[0], res[1]))
			#print "\nPOS------ im.get_size()", im.get_size()
			#self.res
			for i in range(nRots):
				imMod = imBlank.copy()
				imCp = im.copy()
				#print "\n\n\n***** sc", sc, "prog", prog, "rg", rg
				imCp = pygame.transform.scale(imCp, (int(res[0]*sc), int(res[1]*sc)))

				txAbs = tx * res[0]
				tyAbs = ty * res[1]
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
						imMod.blit(thisImCp, (txInt, tyInt), (0, 0, res[0], res[1]), pygame.BLEND_ADD)

				imCpSzOld = imMod.get_size()
				imMod = pygame.transform.rotate(imMod, (i+(.5*(clipNum % 2)) + .002*fr)*360.0/nRots)
				#imMod = pygame.transform.rotate(imMod, i*45)
				imCpSzNew = imMod.get_size()
				xStart = imCpSzOld[0] - imCpSzNew[0]
				yStart = imCpSzOld[1] - imCpSzNew[1]
				imOut.blit(imMod, (0, 0), (-xStart/2, -yStart/2, res[0], res[1]), pygame.BLEND_ADD)

		print "_processImg(): saving", self.outImgPath, "..."
		pygame.image.save(imOut, self.outImgPath)
		self.updateOutImg()
		self.updateClipImgs()
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
				#print "_loadParms(): ln =", ln
				words = ln.split()
				#print "_loadParms(): words =", words
				#print "_loadParms(): len(words) =", len(words)
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
			print "_strValToParmDic(): parmName=", parmName, ", val=", val
			typ = self.parmDic[parmName]["type"]
			if typ == "int":
				self.parmDic[parmName]["val"] = int(val)
			elif typ == "float":
				#print "---------- val", val
				self.parmDic[parmName]["val"] = float(val)
			else:
				self.parmDic[parmName]["val"] = val
				
	def saveUIToParmsAndFile(self, pn=None, sv=None):
		print "_saveUIToParmsAndFile(): pn", pn, "sv", sv
		if not pn == None:
			val = sv.get()
			self.strValToParmDic(pn, val)
		with open(parmFile, "w") as f:
			for parmName in self.parmLs:
				parmVal = self.parmDic[parmName]["val"]
				f.write(parmName + "\n")
				f.write("value " + str(parmVal) + "\n\n")

		renPathParms = renDirKscope + "/" + self.parmVal("renVer") + "/kScopeParms"
		shutil.copyfile(parmFile, renPathParms)
			

	def refreshThumb(self, clipNum):
		# Get ren fr at start, mid, end
		imgDir = self.getImgNumDir(clipNum)
		renImgs = os.listdir(imgDir)
		renImgs.sort()

		self.thumbs[clipNum]["photos"] = []
		for i in range(3):
			# Render 25%, 50%, 75% thru seq
			if renImgs == []:
				imgPath = errorImgPath
			else:
				#thumbImg = renImgs[((1+i)*len(renImgs))/4]
				thumbImg = renImgs[int([.2,.5,.8][i]*len(renImgs))]
				print "\n_refreshThumb(): clip=", self.clipSeq[clipNum], "thumbImg=", thumbImg
				imgPath = imgDir + "/" + thumbImg
			loadedImg = self.safeLoadImg(imgPath)
			loadedImg = self.scaleToHt(loadedImg, displayHt/3)

			photo = ImageTk.PhotoImage(loadedImg)
			self.thumbs[clipNum]["photos"].append(photo)
			self.thumbs[clipNum]["buttons"][i].configure(image=photo)

	
	def setMenuItems(self, menu, var, items, val=None):
		print "_setMenuItems(): items=", items
		print "_setMenuItems(): val=", val
		menu.delete(0, "end")
		for s in items:
			menu.add_command(label=s, command=lambda value=s: var.set(value))
		if val:
			var.set(val)

	def refreshVersParm(self, numStr):
		versParm = "version"  + numStr
		imageParm = "image"  + numStr
		imageVal = self.parmVal(imageParm)
		#print "\n*****Is image, versParm=", versParm
		vers = os.listdir(ut.renDir + "/" + imageVal)
		vers.sort()
		versLast = vers[-1]
		self.strValToParmDic(versParm, versLast)
		#print "-----vers:", vers
		menu = self.parmDic[versParm]["ui"]["optionmenu"]["menu"]
		self.setMenuItems(menu, self.parmDic[versParm]["ui"]["var"], vers, versLast)
		#menu.delete(0, "end")
		#for s in vers:
		#	menu.add_command(label=s, command=lambda value=s: self.parmDic[versParm]["ui"]["var"].set(value))

		#self.parmDic[versParm]["ui"]["var"].set(versLast)


	def menuImgChooser(self, selection, imgParmName, numStr):
		#print "_menuImgChooser(): self.imgChooserVar.get()", self.imgChooserVar.get(), "selection", selection, "numStr", numStr
		print "_menuImgChooser(): imgParmName", imgParmName, "selection", selection, "numStr", numStr
		self.strValToParmDic(imgParmName, selection)

		if imgParmName[:5] == "image":
			self.refreshVersParm(numStr)



		clipNum = imgParmName[-1]
		#im = self.loadImgNum(clipNum)
		self.refreshThumb(int(clipNum))
		self.saveUIToParmsAndFile()
		self.setLabelText(int(clipNum))

	def menuVerChooser(self, selection):
		print "_menuImgChooser(): self.verChooserVar.get()", self.verChooserVar.get(), "selection", selection

	def menuRenVerChooser(self, selection):
		print "_menuRenImgChooser(): self.renDirVar.get()", self.renDirVar.get(), "selection", selection
		#self.strValToParmDic("renVer", selection)
		self.saveUIToParmsAndFile("renVer", self.renDirVar)
		self.updateOutImg()

	def menuResChooser(self, selection):
		print "_menuResChooser(): self.resVar.get()", self.resVar.get(), "selection", selection
		#self.strValToParmDic("renVer", selection)
		self.saveUIToParmsAndFile("res", self.resVar)
		self.setRes()
		self.updateOutImg()


	def makeParmLabelEntry(self, parmName, frame, row):
		parmVal = self.parmDic[parmName]["val"]
		label = Label(frame, width=10, text=parmName)
		label.grid(row=row)

		entry = Entry(frame, width=10)
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

		self.entryDic[entry] = parmName

	def clipRngAndSeqRng(self, clipNum):
		clip = self.clipSeq[clipNum]
		clipRng = clipDic[clip]["range"]
		ofs = self.clipSeqOfs[clipNum]
		return clipRng, (clipRng[0] - ofs, clipRng[1] - ofs)
		

	def setLabelText(self, clipNum):
		print "_setLabelText(): clipNum=", clipNum
		clipRng, seqRng = self.clipRngAndSeqRng(clipNum)
		text="C %d, %d fr, src: %d-%d, out: %d-%d" % ((clipNum, clipRng[1]-clipRng[0]) + clipRng + seqRng)
		self.clipInfoLabels[clipNum].configure(text=text)

	def setRes(self):
		resStr = self.parmVal("res")
		resStrLs = resStr.split("x")
		print "\n\n resStr", resStr, "resStrLs", resStrLs
		self.res = (int(resStrLs[0]), int(resStrLs[1]))

	def btnClip(self, clipNum):
		seqRng = self.clipRngAndSeqRng(clipNum)[1]
		print "_btnClip(): clipNum=", clipNum, "seqRng", seqRng
		self.processImgSeq(seqRng)
		

	def __init__(self):
# CONROL THUMBNAIL LAYOUT goes a little like this:
		comment = """
contols0a	thumbs0a(0,1)	thumbAt0midpoint	thumbs1a(0,1)	contols1a
contols0b	thumbs0a(2,3)	thumbAt1midpoint	thumbs1a(2,3)	contols1b

contols2a	thumbs2a(0,1)	thumbAt2midpoint	thumbs3a(0,1)	contols3a
contols2b	thumbs2a(2,3)	thumbAt3midpoint	thumbs3b(2,3)	contols3a

contols4a	thumbs4a(0,1)	thumbAt4midpoint	thumbs5a(0,1)	contols5a
contols4b	thumbs4a(2,3)	thumbAt5midpoint	thumbs5b(2,3)	contols5a
"""

		self.entryDic = {}

		self.root = Tk()
		#self.root.bind('<Escape>', lambda e: self.root.destroy())
		self.root.bind('<Escape>', lambda e: self.hkEsc())

		self.frameMaster = Frame(self.root)
		self.frameMaster.grid()
		self.frameClips = Frame(self.frameMaster)
		self.frameClips.grid(row=0, column=0)

		self.frameClipL = Frame(self.frameClips, highlightcolor="red", highlightthickness=1,highlightbackground="green",bd=1)
		self.frameClipL.grid()

		self.frameClipM = Frame(self.frameClips, highlightcolor="red", highlightthickness=1,highlightbackground="green",bd=1)
		self.frameClipM.grid(row=0, column=1)

		self.frameClipR = Frame(self.frameClips, highlightcolor="red", highlightthickness=1,highlightbackground="green",bd=1)
		self.frameClipR.grid(row=0, column=2)



		self.frameR = Frame(self.frameMaster)
		self.frameR.grid(row=0, column=1)

		self.frameCtls = Frame(self.frameR)
		self.frameCtls.grid(row=1, column=0)


		#self.frameCtlsPreClip = Frame(self.frameR)
		#self.frameCtlsPreClip.grid()

		self.frameImgs = Frame(self.frameClips)
		#self.frameImgs.grid(row=0,column=1)

		# Load parms
		self.loadParms(True)
		self.loadParms(False)

		#self.res = (960, 540)
		#self.res = resOptions[self.parmVal("res")]
		self.setRes()


		# Set up clips
		self.nClips = 6
		self.makeClipSeq()
		self.makeClipFrOfs()
		
		# Controls
		self.thumbs = {}
		row = 0

		BEParms = ["tx", "ty", "sc"]

		self.renderedClips = os.listdir(ut.renDir)
		self.renderedClips.sort()

		self.resVar = StringVar()
		self.resVar.set(self.parmVal("res"))
		#options = ["a", "bb"]
		self.resChooser = OptionMenu(self.frameCtls, self.resVar, *resOptions, command=self.menuResChooser)
		self.resChooser.grid(row=row, column=0)
		row += 1

		self.makeParmLabelEntry("fr", self.frameCtls, row)
		row += 1

		self.renDirVar = StringVar()
		self.renDirVar.set(self.parmVal("renVer"))
		self.renDirVar.trace("w", lambda name, index, mode, sv=self.renDirVar,
			pn="renVerOut": self.saveUIToParmsAndFile(pn, sv))


		renVersions = os.listdir(ut.renDir + "/kScope")
		renVersions.sort()
		renVersions.reverse()
		self.renDirVerChooser = OptionMenu(self.frameCtls, self.renDirVar, *renVersions, command=self.menuRenVerChooser)
		self.renDirVerChooser.grid(row=row)

		self.nextRenVerEntry = Entry(self.frameCtls, width=10)
		#self.entries.append(self.nextRenVerEntry)
		self.entryDic[self.nextRenVerEntry] = "renVerOut"
		self.nextRenVerEntry.grid(row=row, column=1)
		row += 1

		rowLR = [0, 0]

		self.clipInfoLabels = [None] * self.nClips
		print "\n\n88888888888 self.clipInfoLabels", self.clipInfoLabels

		# Controls per clip
		for clipNum in range(self.nClips):
			clipNumStr = str(clipNum)
			isOdd = clipNum % 2
			if isOdd == 0:
				frameThisClipParmsAndThumb = Frame(self.frameClipL, highlightcolor="red", highlightthickness=1,highlightbackground="green",bd=1)
			else:
				frameThisClipParmsAndThumb = Frame(self.frameClipR, highlightcolor="red", highlightthickness=1,highlightbackground="green",bd=1)
			frameThisClipParmsAndThumb.grid(row=rowLR[isOdd])

			frameThisClipInfoAndParms = Frame(frameThisClipParmsAndThumb)
			frameThisClipInfoAndParms.grid(column=isOdd)

			# Info

			#clip = self.clipSeq[clipNum]
			#rng = clipDic[clip]["range"]
			#ofs = self.clipSeqOfs[clipNum]

			#label = Label(frameThisClipInfoAndParms,
			#	text=("Clip %d, ranges: src: %d-%d, out: %d-%d" % ((clipNum, ) + rng + (rng[0] - ofs, rng[1] - ofs))))
			label = Label(frameThisClipInfoAndParms)
			label.grid()
			self.clipInfoLabels[clipNum] = label
			self.setLabelText(clipNum)


			frameThisClipParms = Frame(frameThisClipInfoAndParms)
			frameThisClipParms.grid(row=1, column=0)

			thisClipRow = 0



			# Menus
			for menuParm in ["image", "version"]:
				imgParmName = menuParm + clipNumStr
				label = Label(frameThisClipParms, text=imgParmName)
				label.grid(row=thisClipRow)

				clipChooserVal = self.parmVal(imgParmName)
				clipChooserVar = StringVar(frameThisClipParms)
				clipChooserVar.set(clipChooserVal)
			
				selections = self.renderedClips # To be replaced if this is "version"
				clipChooser = OptionMenu(frameThisClipParms, clipChooserVar, *selections,
							command=lambda selection=imgParmName, imgParmName=imgParmName, numStr=clipNumStr : self.menuImgChooser(selection, imgParmName, numStr))
				clipChooser.grid(row=thisClipRow, column=1)
				
				thisClipRow +=1

				self.parmDic[imgParmName]["ui"] = {
					"label": label,
					"optionmenu": clipChooser,
					"var": clipChooserVar,
					}

				if menuParm == "version":
					self.refreshVersParm(clipNumStr)

			# Parms like txB0, txE0, tyB0....
			for BEParm in BEParms:
				for BE in "BE":
					parmName = BEParm + BE + clipNumStr
					self.makeParmLabelEntry(parmName, frameThisClipParms, thisClipRow)
					thisClipRow += 1

			# Thumbnail

			buttons = []
			frameButtons = Frame(frameThisClipParmsAndThumb)
			frameButtons.grid(row=0, column=(1-isOdd))
			for i in range(3):
				button = Button(frameButtons)
				button.grid()
				buttons.append(button)
			self.thumbs[int(clipNum)] = {"buttons":buttons}

			self.refreshThumb(int(clipNum))

			rowLR[isOdd] += 1

		# Images
		self.outImgBut = Button(self.frameR)
		self.outImgBut.grid(row=0, column=0)
		self.outImgButs = []
		for clipNum in range(self.nClips):
			button = Button(self.frameClipM, command=lambda args=clipNum : self.btnClip(args), highlightcolor="green", highlightthickness=3,bd=0)
			button.grid(row=clipNum)
			self.outImgButs.append(button)
		self.setClipHighlight()
		self.updateOutImg()
		self.updateClipImgs()
		
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
		self.root.bind('<Up>', lambda e: self.valNudge(.01))
		self.root.bind('<Down>', lambda e: self.valNudge(-.01))
		self.root.bind('<Shift-Up>', lambda e: self.valNudge(.1))
		self.root.bind('<Shift-Down>', lambda e: self.valNudge(-.1))
		self.root.bind('<Alt-Up>', lambda e: self.valNudge(.01, True))
		self.root.bind('<Alt-Down>', lambda e: self.valNudge(-.01, True))
		self.root.bind('<Alt-Shift-Up>', lambda e: self.valNudge(.1, True))
		self.root.bind('<Alt-Shift-Down>', lambda e: self.valNudge(-.1, True))


		print "\n"*5
		for clipNum in range(self.nClips):
			fr = self.parmVal("fr")
			ofs = self.clipSeqOfs[clipNum]
			print "clipNum=", clipNum, ", seq=", self.clipSeq[clipNum], ", ofs", ofs, ", fr=", fr, ", fr+ofs=", fr+ofs

		mainloop() 

kWin()
