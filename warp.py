#!/usr/bin/python
import os, genData, ut, time, datetime, pprint, cProfile, shutil, glob, pygame, fragmod
import numpy as np
import pyopencl as cl
from Tkinter import *
import Tkinter, ttk
import PIL
from PIL import ImageTk, Image
from tkColorChooser import askcolor			  

parmPath = ut.projDir + "/parms"

statsObjPathSrc="/tmp/statsObj"
statsDirDest=""


class warpUi():
	def rebuildUI(self):
		print "\n_rebuildUI(): Reloading........"
		self.saveParmDic()
		ut.exeCmd("python setupFragmod.py build; sudo python setupFragmod.py install")
		ut.exeCmd("killall warp.py; /home/jeremy/dev/warp/warp.py")
		
	def putParmDicInUI(self):
		self.pauseSaveUIToParmsAndFile = True
		print "\n\n_putParmDicInUI(): self.parmDic.parmDic.keys():", self.parmDic.parmDic.keys()
		for k,thisDic in self.parmDic.parmDic.items():
			if "uiElement" in thisDic.keys() and not thisDic["type"] in ["clr", "bool"]:
				uiElement = thisDic["uiElement"]
				uiElement.delete(0, END)
				#val = self.parmDic(k)
				val = thisDic["val"]
				uiElement.insert(0, str(val))

		self.pauseSaveUIToParmsAndFile = False

	def saveUIToParmsAndFile(self, parmName, arg):
		#print "\n_saveUIToParmsAndFile(): self.pauseSaveUIToParmsAndFile =", self.pauseSaveUIToParmsAndFile
		if isinstance(arg, StringVar):
			val = arg.get()
		else:
			val = arg

		if not self.pauseSaveUIToParmsAndFile:
			ints="-0123456789"
			floats= ints + "."
			#for parmName in self.parmDic.parmDic.keys():
			thisDic = self.parmDic.parmDic[parmName]
			# Below is just so we don't make errors before all the
			# ui is built - a bit unsatisfying.
			setVal = True
			typ = thisDic["type"]
			if typ == "int":
				for v in val:
					#print "_saveUIToParmsAndFile(): v", v
					if not v in ints:
						print "_saveUIToParmsAndFile(): ERROR: bad character entered", v
						setVal = False
						break
			elif typ == "float":
				for v in val:
					if not v in floats:
						print "_saveUIToParmsAndFile(): ERROR: bad character entered", v
						setVal = False
						break

			if setVal:
				print "_saveUIToParmsAndFile(): for", parmName, ": setting thisDic['val'] to", val
				thisDic["val"] = val
				if parmName == "fr":
					self.setFrAndUpdate(val)
			else:
				val = thisDic["val"]
				print "_saveUIToParmsAndFile(): re setting entry to ", val;
				self.parmDic.parmDic[parmName]["uiElement"].delete(0, END)
				self.parmDic.parmDic[parmName]["uiElement"].insert(0, str(val))
			print "\n\n_saveUIToParmsAndFile(): END, about to do saveParmDic"
			self.saveParmDic()
		self.updateBreaths()


	def btn_getColor(self, args):
		k,c = args
		print "\n_btn_getColor(): k:", k, ", c:", c
		c = self.parmDic(k)
		hx = ut.rgb_to_hex(c)
		print "_btn_getColor(): c:", c
		print "_btn_getColor(): hx:", hx
		color = askcolor(color=hx) 
		print "_btn_getColor(): color", color
		if color:
			clrInt = color[0]
			clrDec = ut.rgb_int_to_dec(clrInt)
			print "_btn_getColor(): clrDec", clrDec
			self.setVal(k, clrDec)
			postC = self.parmDic(k)
			print "_btn_getColor(): postC", postC
			self.parmDic.parmDic[k]["uiElement"].configure(bg=color[1])
		self.makeCInOutValsLs()
	
	def notebookTabChange(self, event):
		print "Tab Changed.", event
		self.frameMaster.focus_set()

	def makeParmUiElement(self, parmName, thisFrame, thisRow, thisCol, labTxt=None):
		thisParmDic = self.parmDic.parmDic[parmName]
		if thisParmDic["type"] == "bool":
			self.chkVars[parmName] = IntVar()
			self.chkVars[parmName].set(self.parmDic(parmName))
			ent = Checkbutton(thisFrame, variable=self.chkVars[parmName], command=lambda pn=parmName: self.chk_cmd(pn))
		else:
			ent = Entry(thisFrame, width=5)
			sv = StringVar()
			sv.trace("w", lambda name, index, mode, sv=sv,
				pn=parmName: self.saveUIToParmsAndFile(pn, sv))
			ent.configure(textvariable=sv)
			ent.insert(0, str(thisParmDic["val"]))

		txt = parmName if labTxt == None else labTxt
		lab = Label(thisFrame, text=txt)
		lab.grid(row=thisRow, column=thisCol, sticky=E)
		ent.grid(row=thisRow, column=(thisCol+1), sticky=W)

		thisParmDic["uiElement"] = ent

		return ent


	def makeParmUi(self, startRow):
		row = startRow
		self.nbExclude = ttk.Frame(self.frameParmAndControls)
		self.nbExclude.grid(row=1)
		self.nbParm = ttk.Notebook(self.frameParmAndControls)
		self.nbParm.bind("<<NotebookTabChanged>>", self.notebookTabChange)
		self.nbParm.grid(row=2)
		self.nbFrames = {}
		#stages = self.parmDic.parmStages.keys()
		#stages.sort() # Just to get GEN in front of REN
		#TODO make this dynamically depend on parms file
		stages = ["META", "GEN", "REN", "CLR", "AOV"]
		parmsToShowInMeta = ["isoLev", "tripAlwaysOn"]
		for stage in stages:
			if not stage == "META":
				self.nbFrames[stage] = ttk.Frame(self.nbParm)
				self.nbParm.add(self.nbFrames[stage], text=stage)
		maxCNum = 0

		clrParmDicDic = {}
		rClmMetaRow = row
		for parmName,dic in self.parmDic.parmLs: # Recall: parmLs = [("parmName", {'key':val...}]
			thisParmDic = self.parmDic.parmDic[parmName]
			print "_makeParmUi(): parmName:", parmName, ", thisParmDic:", thisParmDic
			
			if "hidden" in thisParmDic.keys() and thisParmDic["hidden"] == "True":
				print "_makeParmUi(): HIDDEN, skipping..."
				continue

			thisRow = row
			colOfs = 0

			isRClmMetaParm = (parmName in parmsToShowInMeta or parmName == "frIncRen")

			if isRClmMetaParm:
				thisStage = "META"
				colOfs = 2
				thisRow = rClmMetaRow
			else:
				thisStage = thisParmDic["stage"]

			print "_makeParmUi(): \t thisStage:", thisStage
			if thisStage == "META":
				thisFrame = self.nbExclude
			else:
				thisFrame = self.nbFrames[thisStage]



			if thisStage == "CLR":
				clrParmDicDic[parmName] = dic
			else:

				ent = self.makeParmUiElement(parmName, thisFrame, thisRow, colOfs)

				# Add entry to dic of corresponding types.
				if thisParmDic["type"] in self.parmEntries.keys():
					self.parmEntries[thisParmDic["type"]].append(ent)
				else:
					self.parmEntries[thisParmDic["type"]] = [ent]

				if isRClmMetaParm:
					rClmMetaRow += 1
				else:
					row += 1

		# CLRs
		row = startRow
		clrGrpRow = 0
		thisFrame = self.nbFrames["CLR"]
		#for parmName,dic in clrParmDicDic:

		srcPath = self.images["source"]["path"]
		#path = "/home/jeremy/dev/warp/seq/lgP6/lgP6.03409.png"
		pathSpl = srcPath.split("/")
		leaf = pathSpl[-1]
		leafSpl = leaf.split(".")

		thumbYRes = 60
		thumbResRatio = float(thumbYRes)/self.res[1]
		thumbRes = (int(self.res[0]*thumbResRatio), thumbYRes)

		self.pImgs = []


		for breath in range(4):
			for inOut in ["In", "Out"]:
				parmNameNoRGB = "c" + inOut + str(breath)
				clrGrpFrame = Frame(thisFrame)
				clrGrpFrame.grid(row=clrGrpRow, column=1)
				rowFrameTop = Frame(clrGrpFrame)
				rowFrameTop.grid(row=0, column=1, sticky=EW)

				inhExh = "inh" if inOut == "In" else "exh"
				parmNameFr = inhExh + str(breath)
				ent = self.makeParmUiElement(parmNameFr, rowFrameTop, 0, 0)

				parmNameFrTrip = parmNameFr + "trip"
				ent = self.makeParmUiElement(parmNameFrTrip, rowFrameTop, 0, 2, labTxt="trp")

				rowFrameBot = Frame(clrGrpFrame)
				rowFrameBot.grid(row=1, column=1)
				col = 1

				rgbVals = []
				for rgb in "RGB":
					parmName = parmNameNoRGB + rgb
					#thisRow = cNum * 4 + ("RGB".index(cRGB) + 1)
					clrTuple = self.parmDic(parmName)
					rgbVals.append(clrTuple)
					hx = ut.rgb_to_hex(clrTuple)
					ent = Button(rowFrameBot, width=1, bg=hx,command=lambda
						args=(parmName,clrTuple): self.btn_getColor(args))

					#lab.grid(row=thisRow, column=colOfs, sticky=E)
					ent.grid(row=0, column=(col), sticky=E)
					thisParmDic["uiElement"] = ent
					col += 1

					# Add entry to dic of corresponding types.
					if thisParmDic["type"] in self.parmEntries.keys():
						self.parmEntries[thisParmDic["type"]].append(ent)
					else:
						self.parmEntries[thisParmDic["type"]] = [ent]

					self.parmDic.parmDic[parmName]["uiElement"] = ent

				# Add black and white.

				#col = 1
				hx = ut.rgb_to_hex((0, 0, 0))
				ent = Button(rowFrameBot, width=1, bg=hx,command=lambda
					args=(parmName,clrTuple): self.btn_getColor(args))
				ent.grid(row=0, column=col, sticky=W)

				white = [0,0,0]
				rAr = np.array(rgbVals[0], dtype=np.float32)
				gAr = np.array(rgbVals[1], dtype=np.float32)
				bAr = np.array(rgbVals[2], dtype=np.float32)
				whiteAr = np.array(white, dtype=np.float32)

				fragmod.cspace(rAr, gAr, bAr, whiteAr)
				#dud,breaths,dud = zip(*self.breathsNameFrTrip)
				#breathsAr = np.array(breaths, dtype=np.intc)
				#fr = self.parmDic("fr")
				#test = fragmod.calcInRip(fr, breathsAr, len(breaths), 0, .5)
				#print "\n"*10 + "JJJJJJJJJJJ test", test

				hx = ut.rgb_to_hex(whiteAr)
				#hx = ut.rgb_to_hex((.5, .5, .5))
				butThumFrame = Frame(thisFrame)
				butThumFrame.grid(row=clrGrpRow, column=2)
				ent = Button(butThumFrame, height=3, width=1, bg=hx,command=lambda
					args=(parmName,clrTuple): self.btn_getColor(args))
				#ent.grid(row=0, column=col, sticky=W)
				
				col = 0 if inOut == "In" else 1
				ent.grid(row=0, column=col)


				# Add thumbnail
				# loadedImg = Image.open(path)
				# loadedImg = loadedImg.resize((res[0], res[1]))
				# img = ImageTk.PhotoImage(loadedImg)

				#ht = self.images["source"]["pImg"].height()
				#sc = float(30)/ht
				#pImg.resize((50, 30))
				#pImg = self.images["source"]["pImg"].zoom(sc,sc)
				brFr = self.parmDic(parmNameFr)
				#brFr = self.parmDic("frStart") # No more breaths
				brFr = min(3200, brFr)
				leafSpl[-2] = "%05d" % brFr
				leafThisBr = ".".join(leafSpl)
				pathSpl[-1] = leafThisBr
				pathThisBr = "/".join(pathSpl)
				#img = Image.open(pathThisBr)
				if not os.path.exists(pathThisBr):
					pathThisBr = self.errorImgPath

				#img = img.resize(thumbRes, Image.ANTIALIAS)
				imgSrf = pygame.image.load(pathThisBr)
				imgSrf = pygame.transform.scale(imgSrf, thumbRes)

				# Just in/out clr approximation
				inOutBoth = 1 if inOut == "Out" else 0
				#csImg = imgSrf
				csImg,dud = genData.imgToCspace(self, imgSrf, pathThisBr,
					frIn=brFr, inOutBoth=inOutBoth)

				imgPath = ut.imgDir + "/" + parmNameNoRGB + "_justInOrOut.png"
				pygame.image.save(csImg, imgPath)
				pImg = ImageTk.PhotoImage(Image.open(imgPath))
				self.pImgs.append(pImg)

				ent = Label(butThumFrame, image=pImg)
				col = 1 if inOut == "In" else 0
				ent.grid(row=0, column=col)


				# Full clr approximation
				csImg,dud = genData.imgToCspace(self, imgSrf, pathThisBr, frIn=brFr)

				imgPath = ut.imgDir + "/" + parmNameNoRGB + ".png"
				pygame.image.save(csImg, imgPath)
				pImg = ImageTk.PhotoImage(Image.open(imgPath))
				self.pImgs.append(pImg)

				ent = Label(thisFrame, image=pImg)
				ent.grid(row=clrGrpRow, column=3)


				clrGrpRow += 1


		#for dividerNum in range(maxCNum+1):
		#	thisFrame = self.nbFrames["CLR"]
		#	lab = Label(thisFrame, font=("Helvetica", 4), text="-")
		#	#print "\n UUUUUUUUUUUUUUUU font", lab.font
		#	lab.grid(row=(dividerNum+1)*4)



		#print "\n\n_makeParmUi(): parmDic"
		#for k,v in self.parmDic.parmDic.items():
		#	print "_makeParmUi(): \t", k, v["val"]
		#print "\n\n_makeParmUi(): parmLs:", self.parmDic.parmLs
		self.nbParm.select(1)
		return row
		

	def positionWindow(self):
		#w = 1800 # width for the Tk root
		#h = 950 # height for the Tk root
		w = 1800 # width for the Tk root
		h = 1200 # height for the Tk root

		# get screen width and height
		ws = self.root.winfo_screenwidth() # width of the screen
		hs = self.root.winfo_screenheight() # height of the screen

		# calculate x and y coordinates for the Tk root window
		x = 0
		y = 0
		#x = ws - (w/2)
		#y = hs - (h/2)

		# set the dimensions of the screen 
		# and where it is placed
		self.root.geometry('%dx%d+%d+%d' % (ws, hs, x, y))


	def getDbImgParmNames(self):
		aovNames = []
		root = "dbImg"
		for k in self.parmDic.parmDic.keys():
			if k[:len(root)] == root:
				aovNames.append(k)
		print "\n_getDbImgParmNames() aovNames:", aovNames
		aovNames.sort()
		return aovNames
	
	def reloadErrorImg(self):
		errorImg = Image.open(self.errorImgPath)
		errorImg = errorImg.resize((self.displayRes[0], self.displayRes[1]), Image.ANTIALIAS)
		self.staticImages["error"] = ImageTk.PhotoImage(errorImg)



	def loadImages(self):
		# TODO: I expect at least looking up thisImgPath from ut
		# is wrong -- I think they all get overwritten.

		for k in self.getDbImgParmNames():
			lev = self.parmDic("lev_" + k)
			path = self.getDebugDirAndImg(self.parmDic(k), lev)[1]
			print "\n_loadImages(): k:", k, ", path", path
			self.images[k]= {"path":path}


		imgPath = self.getSourceImgPath()
		self.images["source"] = {"path":imgPath}
		self.images["ren"] = {"path":imgPath.replace("/seq/","/ren/")}

		self.images["anim"] = {"pImg":self.staticImages["play"]}
		self.images["rec"] = {"pImg":self.staticImages["recOff"]}

		print "_loadImages(): images:"
		for i,k in self.images.items():
			print i, k

		for img in self.images.keys():
			if not img in (self.staticImageNames + self.varyingStaticImageNames):
				path = self.images[img]["path"]
				print "_loadImages(): Checking existence of", path
				setRes = img == "source"
				big = img in ["source", "ren"]
				self.images[img]["pImg"] = self.loadImgAndSetRes(path, setRes=setRes, big=big)

		res = (self.images["source"]["pImg"].width(), self.images["source"]["pImg"].height())

		#image = self.images["source"]["pImg"]
		#self.res = (image.width(), image.height())
		
		self.reloadErrorImg()

		return res

	def refreshPhotoImages(self):
		# TODO you shouldn't have to reload ALL images eg. play, pause - maybe
		# keep those images "on hand" as PhotoImages that you switch between
		for k,thisDic in self.images.items():
			if not k in (self.staticImageNames + self.varyingStaticImageNames):
				big = k in ["source", "ren"]
				pImg = self.loadImgAndSetRes(thisDic["path"], big=big)
				if k in self.images.keys():
					self.images[k]["pImg"] = pImg
				else:
					self.images[k]= {"pImg":pImg}


	def makeImgButton(self, name, frameParent):
		print "\n_makeImgButton(): name: ", name
		pImg = self.images[name]["pImg"]
		thisButton = Button(frameParent, image=pImg, command=lambda:self.imgButCmd())
		self.images[name]["button"] = thisButton
		return thisButton


	def refreshButtonImages(self): 
		self.refreshPhotoImages()
		dontChange = self.staticImages.keys() + self.varyingStaticImageNames 
		#print "_refreshPhotoImages(): dontChange", dontChange
		for butName,butDic in self.images.items():
			#print "_refreshPhotoImages(): butName:", butName, "butDic", butDic
			if not butName in dontChange and "button" in butDic.keys():
				#print "_refreshPhotoImages(): B"
				butDic["button"].configure(image=butDic["pImg"])


	def imgButCmd(self):
		self.updateCurImg(forceRecord=True)
		self.updateDebugImg()
		self.sortStats()

	def setFrAndUpdate(self, fr):
		self.setStatus("busy")
		self.setVal("fr", fr)
		self.saveParmDic()
		self.updateRenAndDataDirs() # TODO - must this be here?
		# This is what generates data/renders for each fr.
		self.updateCurImg()
		self.updateDebugImg()
		Tk.update_idletasks(self.root)
		

	def ctlReturnCmd(self):
		focused = self.frameMaster.focus_get()
		print "_returnCmd(): focused:", focused
		print "_returnCmd(): self.verUI[ren][sfx]:", self.verUI["ren"]["sfx"]
		if focused == self.verUI["ren"]["sfx"]:
			print "_returnCmd(): \tIT'S REN!!!!!!!!"
			self.butVNew("ren")
			self.saveUIToParmsAndFile("renVer", self.parmDic("renVer"))
		elif focused == self.verUI["data"]["sfx"]:
			print "_returnCmd(): \tIT'S DATA!!!!!!!!"
			self.butVNew("data")
			self.saveUIToParmsAndFile("dataVer", self.parmDic("dataVer"))
			self.verUI["ren"]["sfx"].delete(0, END)
			text = self.verUI["data"]["sfx"].get()
			self.verUI["ren"]["sfx"].insert(0, text)
			self.butVNew("ren")
			self.saveUIToParmsAndFile("renVer", self.parmDic("renVer"))
		else:
			print "_returnCmd(): \tIT'S NEITHER!!!!!!!!"
		self.frameMaster.focus_set()

	def shiftReturnCmd(self):
		self.updateDebugImg()
		genData.renBg(self)
		self.refreshButtonImages()

	def returnCmd(self):
		self.frameMaster.focus_set()

	def execHotkey(self, v):
		focused = self.frameMaster.focus_get()
		dataType = None
		for typ,ents in self.parmEntries.items():
			if focused in ents:
				print "_execHotkey():\tdata typ:", typ
				dataType = typ
				break
		key = v.keysym
		if dataType in ["int", "float", "str"]: 
			if key == "Escape":
				self.returnCmd()
		else:
			print "_execHotkey():\tkey:", key
			if key == "Escape":
				print "\nClosing window, destroying the root!  Bye.\n\n"
				self.rootDestroyed = True
				self.root.destroy()
			elif key == "Left":
				self.setFrAndUpdate(self.parmDic("fr") - 1)
			elif key == "Right":
				self.setFrAndUpdate(self.parmDic("fr") + 1)
			elif key == "Control-Left":
				self.setFrAndUpdate(self.parmDic("frStart"))
			elif key == "Control-Right":
				self.setFrAndUpdate(self.parmDic("frEnd"))
			elif key == "space":
				self.animButCmd()
			elif key == "r":
				self.recButCmd()
			elif key == "c":
				self.toggleDoRenCv()
			elif key == "g":
				self.toggleGenRen1fr()
			elif key == "x":
				self.imgButCmd()

	def stepFwdButCmd(self):
		self.setFrAndUpdate(self.parmDic("fr") + 1)

	def rewButCmd(self):
		self.setFrAndUpdate(self.parmDic("frStart"))

	def ffwButCmd(self):
		self.setFrAndUpdate(self.parmDic("frEnd"))

	def getPrevBr(self, fr):
		prevFr = fr
		prevTripVal = self.breathsNameFrTrip[0][2]
		#breathFramesRev = self.breathFrames[:]
		breathsNameFrTripRev = self.breathsNameFrTrip[:]
		breathsNameFrTripRev.reverse()
		# Append implicit first breath at start of seq.
		breathsNameFrTripRev.append(("dudName", self.parmDic("frStart"), 0))
		#print "\n\n\n HHHHHHHHHHHHHHHH breathsNameFrTripRev", breathsNameFrTripRev
		for br in breathsNameFrTripRev:
			brFr = br[1]
			if brFr < prevFr:
				prevFr = brFr
				prevTripVal = br[2]
				break
		return prevFr, prevTripVal

	def shiftLeftCmd(self):
		thisFr = self.parmDic("fr")
		thisFr,dud = self.getPrevBr(thisFr)
		self.setFrAndUpdate(thisFr)

	def getNextBr(self, fr, incl=False):
		nextBrFr = fr
		nextTripVal = self.breathsNameFrTrip[-1][2]
		for br in self.breathsNameFrTrip:
			brFr = br[1]
			if brFr > nextBrFr or (incl and brFr == nextBrFr):
				nextBrFr = brFr
				nextTripVal = br[2]
				break
		return nextBrFr, nextTripVal

	def shiftRightCmd(self):
		thisFr, dud = self.getNextBr(self.parmDic("fr"))
		thisFr = min(3200, thisFr)
		self.setFrAndUpdate(thisFr)

	def animButCmd(self):
		if self.parmDic("anim") == 0:
			self.setVal("anim", 1)
			# If you're animating and recording and doGen == 0, turn on doRenCv
			if self.record and self.parmDic("doGen") == 0:
				self.setVal("doRenCv", 1)
				self.chk_doRenCv_var.set(1)

			self.timeStart = time.time()
			self.frStartAnim = self.parmDic("fr")
			self.updateCurImg()
		else:
			self.turnAnimOff()
			print "_refreshButtonImages(): self.images:"
			print "_refreshButtonImages():",  self.images
			#self.images["anim"]["button"].configure(image=self.staticImages["play"])

		# Update image
		if self.parmDic("anim") == 1:
			self.images["anim"]["button"].configure(image=self.staticImages["pause"])
		else:
			print "_refreshButtonImages(): self.images:"
			print "_refreshButtonImages():",  self.images
			self.images["anim"]["button"].configure(image=self.staticImages["play"])

		print "_animButCmd(): Pressed anim button, anim set to", self.parmDic("anim")



	def recButCmd(self, val=None):
		if val == None:
			self.record = not self.record
		else:
			self.record = val
		print "_recButCmd(): self.record =", self.record

		# Update image
		if self.record:
			self.images["rec"]["button"].configure(image=self.staticImages["recOn"])
		else:
			self.images["rec"]["button"].configure(image=self.staticImages["recOff"])



	def toggleGenRen1fr(self):
		print "\n\n_toggleGenRen1fr(): BEGIN"
		if self.chk_genRen1fr_var.get() == 1:
			val = 0
		else:
			val = 1
		self.chk_genRen1fr_var.set(val)
		self.chk_genRen1fr_cmd()
		print "_toggleGenRen1fr(): END"

	def toggleDoRenCv(self):
		print "\n\n_toggleDoRenCv(): BEGIN"
		if self.chk_doRenCv_var.get() == 1:
			val = 0
		else:
			val = 1
		self.chk_doRenCv_var.set(val)
		self.chk_doRenCv_cmd()
		print "_toggleDoRenCv(): BEGIN"

	def saveParmDic(self):
		# TODO THIS GETS CALLED WAY TOO MUCH
		#print "_saveParmDic(): BEGIN"
		# TODO Maybe don't hardwire this, user can config it in parmfile
		pathsAndStages = [(parmPath, ["META", "GEN", "REN", "CLR", "AOV"])]
		#print "_saveParmDic(): self.seqDataVDir:", self.seqDataVDir, "for GEN -- ",
		# TODO Shouldn't seqDataVDir and seqRenVDir always exist?
		if os.path.exists(self.seqDataVDir):
			pathsAndStages.append((self.seqDataVDir + "/parms", ["GEN"]))
		#	print "EXISTS"
		#else:
		#	print "DOES NOT EXIST"

		#print "_saveParmDic(): self.seqRenVDir:", self.seqRenVDir, "for REN -- ",
		if os.path.exists(self.seqRenVDir):
			pathsAndStages.append((self.seqRenVDir + "/parms", ["META", "REN", "CLR"]))
		#	print "EXISTS"
		#else:
		#	print "DOES NOT EXIST"

		#print "_saveParmDic(): self.parmDic.parmStages:"
		#for k,v in self.parmDic.parmStages.items():
		#	print "_saveParmDic():\t", k, ":", v

		#print "\n\n_saveParmDic(): parmLs:"
		#for pm in self.parmDic.parmLs:
		#	print "_saveParmDic():", pm
		#print

		for path, stages in pathsAndStages:
			# print "_saveParmDic(): path", path, "stages", stages
			with open(path, 'w') as f:
				for stage in stages:
					f.write("\n\n\n---" + stage + "---\n\n")

					for parm in self.parmDic.parmStages[stage]:
						# fr and image only go in the top level, shared parm file
						if ((stage == "META" and path == parmPath)
								or not parm in ["fr", "image"]):
							f.write(parm + "\n")
							thisDic = self.parmDic.parmDic[parm]
							keys = thisDic.keys()
							keys.sort()
							for attr in keys:
								if not attr in ["uiElement", "stage", "type", "hidden"]:
									 f.write(attr + " " + str(thisDic[attr]) + "\n")
							f.write("\n")
		#print "_saveParmDic(): END"


	def updateDebugImg(self):
		print "\n_updateDebugImg(): BEGIN"
		for i in range(2):
			img = self.parmDic("dbImg" + str(i+1))
			lev = -1 if img[-6:] == "_ctest" else self.parmDic("lev_dbImg" + str(i+1))
			dbImgPath = self.getDebugDirAndImg(img, lev)[1]
			print "\n\n ************** img", img, "lev", lev, "dbImgPath", dbImgPath, "\n\n"
			self.images["dbImg" + str(i+1)]["path"] = dbImgPath
			self.setVal("dbImg" + str(i+1), img)
			print "_updateDebugImg(): dbImgPath", dbImgPath
		self.refreshButtonImages()
		print "_updateDebugImg(): END"

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
			imgSplit = img.split(".")
			thisFr = int(imgSplit[-2])
			if thisFr < mn:
				mn = thisFr
			if thisFr > mx:
				mx = thisFr

		#fr = ut.clamp(fr, mn, mx)
		self.seqStart = mn
		#self.frStartAnim = fr
		self.seqEnd = mx
		self.setVal("fr", fr)

		imgWithFrame = ".".join(imgSplit[:-2]) + (".%05d." % fr) + imgSplit[-1]
		return ut.seqDir + "/" + self.parmDic("image") + "/" + imgWithFrame

	def updateCurImg(self, forceRecord=False):

		# Get levsToRen
		nLevels = self.parmDic("nLevels")
		isoLevStr = self.parmDic("isoLev")
		if "-" in isoLevStr:  # TODO maybe add , syntax: 1-3,5
			if isoLevStr[0] == "-":
				self.levsToRen = range(nLevels)
			else:
				mn,mx = isoLevStr.split("-")
				self.levsToRen = range(int(mn), int(mx) +1)
		else:
			self.levsToRen = [int(isoLevStr)]
		print "_updateCurImg(): self.levsToRen:", self.levsToRen


		print "_updateCurImg(): self.parmDic(image)", self.parmDic("image")
		self.images["source"]["path"] = self.getSourceImgPath()
		print "_updateCurImg(): self.images[source][path]:", self.images["source"]["path"]
		dud, renImgPath = self.getRenDirAndImgPath("ren", "ALL")
		self.images["ren"]["path"] = renImgPath
		print "\n_updateCurImg(): PATH TO RENDER:", renImgPath
		self.setFillMode()
		self.fillMode = "overwrite"
		if self.parmDic("frIncRen") == 0:
			self.fillMode = "fill"
		elif self.parmDic("frIncRen") < 0:
			self.fillMode = "onlyBg"
		print "\n_updateCurImg(): self.fillMode:", self.fillMode
		skip = False
		if self.fillMode == "onlyBg":
			skip = True
		elif self.fillMode == "fill":
			print "_updateCurImg():\tChecking existence of renderered image...",
			if os.path.exists(renImgPath):
				print "Exists.  Skipping render..."
				skip = True
			else:
				print "Doesn't exist, rendering..."


		print "\n_updateCurImg(): self.record", self.record, "; skip", skip

		ut.safeRemove(genData.outFile)
		genData.pOut("\nPRE genData")

		# Render BG img.
		#if self.record: genData.renBg(self)

		if ((not skip) and self.record) or forceRecord:
			genData.pOut("doing genData")
			reload(genData)
			self.setStatus("busy", "Doing genData...")
			ut.timerStart(self, "genData")

			######## THIS IS WHERE DATA GETS GENERATED ########
			genData.genData(self, self.seqRenVDir)
			###################################################

			ut.timerStop(self, "genData")
			print "\n_updateCurImg(): Done genData\n\n"
			self.setStatus("idle")
		else:
			genData.pOut("skipping genData")


		self.refreshButtonImages()
		self.setStatus("idle")


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
		print "\n\n_getImg(): selection:",  selection, ", debugNum:", debugNum
		if debugNum:
			self.setVal("dbImg" + str(debugNum), selection)
			self.updateRenAndDataDirs()
			self.updateDebugImg()
		elif debugNumLev:
			self.setVal("lev_dbImg" + str(debugNumLev), selection)
			self.updateRenAndDataDirs()
			self.updateDebugImg()
		else:
			print "_getImg(): ################ setting selection:", selection
			#if self.record:
			#	# Turn off recording so you don't render right away.
			#	self.recButCmd()
			initRecordVal = self.record
			self.record = False
			self.setVal("image", selection) #TODO: Rename image to maybe seqName?
			self.updateRenAndDataDirs()
			self.updateCurImg()
			self.updateDebugImg()
			self.record = initRecordVal

	def repopulateMenu(self, verType, vers):
		menu = self.verUI[verType]["OptionMenu"]["menu"]
		menu.delete(0, "end")
		for s in vers:
			menu.add_command(label=s, command=lambda value=s: self.verUI[verType]["menuVar"].set(value))

	def menuImgChooser(self, selection):
		print "\n_menuImgChooser(): pre _getImg"
		print "_menuImgChooser(): self.seqDataDir", self.seqDataDir
		print "_menuImgChooser(): self.seqDataVDir", self.seqDataVDir
		print "_menuImgChooser(): self.seqRenDir", self.seqRenDir
		print "_menuImgChooser(): self.seqRenVDir", self.seqRenVDir
		self.getImg(selection)

		renVers = self.getSeqVersions("ren")
		dataVers = self.getSeqVersions("data")
		verss = {"ren":renVers, "data":dataVers}

		self.seqDataVDir = self.seqDataDir + "/" + dataVers[0]
		self.seqRenVDir = self.seqRenDir + "/" + renVers[0]
		print "\n_menuImgChooser(): post _getImg"
		print "_menuImgChooser(): self.seqDataDir", self.seqDataDir
		print "_menuImgChooser(): self.seqDataVDir", self.seqDataVDir
		print "_menuImgChooser(): self.seqRenDir", self.seqRenDir
		print "_menuImgChooser(): self.seqRenVDir", self.seqRenVDir
		print "\n\n"

		verDic = {}

		print "\n\n_menuImgChooser(): self.verUI"
		pprint.pprint(self.verUI)
		for verType in ["ren", "data"]:
			self.repopulateMenu(verType, verss[verType])
			latestVer = verss[verType][0]
			print "_menuImgChooser():\tresetting  latestVer to ", latestVer
			self.verUI[verType]["menuVar"].set(latestVer)
			self.setVal(verType + "Ver", latestVer)


		#TODO remove these lines, replace with parm assignment
		self.setVal("frStart", self.seqStart)
		self.setVal("frEnd", self.seqEnd)


		renParmPath = self.seqRenDir + "/" + renVers[0] + "/parms"
		if os.path.exists(renParmPath):
			print "_menuImgChooser(): loading parms from", renParmPath, "..."
			self.parmDic.loadParms(renParmPath)
		else:
			print "_menuImgChooser(): ^^^", renParmPath, "not found"


		dataParmPath = self.seqDataDir + "/" + dataVers[0] + "/parms"
		if os.path.exists(dataParmPath):
			print "_menuImgChooser(): loading parms from", dataParmPath, "..."
			self.parmDic.loadParms(dataParmPath)
		else:
			print "_menuImgChooser(); ^^^", dataParmPath, "not found"

		self.updateCurImg()
		self.updateDebugImg()
		self.refreshButtonImages()
		self.putParmDicInUI()
		self.saveUIToParmsAndFile("image", selection)
		print "_menuImgChooser(): END - self.images[source][path]:", self.images["source"]["path"]
		

	def menuVChooser(self, selection, verType):
		print "\n_menuVChooser(): selection", selection, "verType", verType
		print "\n\n_menuVChooser(): self.verUI"
		pprint.pprint(self.verUI)
		verNum = selection
		print "_menuVChooser(): OLD:\n\tseqDataDir:", self.seqDataDir, "\n\tseqDataVDir:", self.seqDataVDir, "\n\tseqRenDir", self.seqRenDir, "\n\tseqRenVDir", self.seqRenVDir
		if verType == "data":
			self.seqDataVDir = self.seqDataDir + "/" + verNum
			parmPath = self.seqDataVDir + "/parms"
		else:
			self.seqRenVDir = self.seqRenDir + "/" + verNum
			parmPath = self.seqRenVDir + "/parms"
		print "_menuVChooser(): NEW:\n\tseqDataDir:", self.seqDataDir, "\n\tseqDataVDir:", self.seqDataVDir, "\n\tseqRenDir", self.seqRenDir, "\n\tseqRenVDir", self.seqRenVDir

		if os.path.exists(parmPath):
			print "\n_menuVChooser(): !!! loading parms from", parmPath, "..."
			self.parmDic.loadParms(parmPath)
			self.putParmDicInUI()
		else:
			print "_menuVChooser(): ???", parmPath, "not found"
		print "_menuVChooser(): setting " + verType + "Ver to", verNum
		self.setVal(verType + "Ver", verNum)
		self.updateRenAndDataDirs() #TODO: I don't think this is necessary, it's done above - useful for menuImgChooser
		self.updateCurImg()
		self.updateDebugImg()
		self.saveUIToParmsAndFile(verType + "Ver", verNum)


	def butVNew(self, verType):
		print "\n\n\n_butVNew(): verType\n\n", verType
		#verType = "ren"
		vers = self.getSeqVersions(verType)
		vers.sort()
		vers.reverse()
		latestVer = vers[0]
		print "_butVNew():", verType + "Vers"
		print "_butVNew():", vers
		print "_butVNew():", verType + "Vers[-1]", vers[0]
		print "_butVNew():", verType + "Vers[-1][1:4]", vers[0][1:4]
		nextVerInt = int(latestVer[1:4]) + 1
		print "\n\n_butVNew(): self.verUI"
		pprint.pprint(self.verUI)
		nextVer = ("v%03d" % nextVerInt) + self.verUI[verType]["sfx"].get()

		verDir = self.seqRenDir if verType == "ren" else self.seqDataDir
		ut.mkDirSafe(verDir + "/" + nextVer)
		# Copy parms
		if os.path.exists(self.seqDataVDir + "/parms"):
			shutil.copy2(self.seqDataVDir + "/parms", verDir + "/" + nextVer)

		self.setVal(verType + "Ver", nextVer)

		vers = [nextVer] + vers
		self.repopulateMenu(verType, vers)
		self.verUI[verType]["menuVar"].set(nextVer)
		self.menuVChooser(nextVer, verType)


	def chk_genRen1fr_cmd(self):
		val = self.chk_genRen1fr_var.get()
		print "_chk_genRen1fr_cmd(): Setting self.displayNaturalRes to:", val
		self.genRen1fr = val
		self.updateCurImg()

	def chk_naturalRes_cmd(self):
		val = self.chk_naturalRes_var.get()
		print "_chk_naturalRes_cmd(): Setting self.displayNaturalRes to:", val
		self.displayNaturalRes = val
		self.updateCurImg()

	def setRenCvUIClr(self):
		defaultBg = self.root.cget('bg')
		if self.chk_doRenCv_var.get() == 0:
			self.chk_doRenCv.configure(bg=defaultBg)
		else:
			self.chk_doRenCv.configure(bg="grey")
		

	# TODO: rename to renMode, make it a case of chk_cmd - maybe eventually
	def chk_doRenCv_cmd(self):
		val = self.chk_doRenCv_var.get()
		print "_chk_doRenCv_var(): Setting doRenCv to:", val
		self.setVal("doRenCv", val)
		self.setRenCvUIClr()
		self.saveUIToParmsAndFile("doRenCv", val)

	def chk_cmd(self, parmName):
		val = self.chkVars[parmName].get()
		print "_chk_doRenCv_var(): Setting", parmName, "to:", val
		self.setVal(parmName, val)
		self.saveUIToParmsAndFile(parmName, val)


	def setVal(self, parmStr, val):
		self.pauseSaveUIToParmsAndFile = True
		if "uiElement" in self.parmDic.parmDic[parmStr]:
			uiElement = self.parmDic.parmDic[parmStr]["uiElement"]
			if not self.parmDic.parmDic[parmStr]["type"] in ["clr", "bool"]:
				uiElement.delete(0, END)
				uiElement.insert(0, str(val))
		valStr = str(val)
		if type(val) in [type(()), type([])]:
			valStr = valStr[1:-1].replace(' ','')
		print "_setVal(): setting parmDic[" + parmStr + "] to", valStr
		self.parmDic.parmDic[parmStr]["val"] = valStr
		self.pauseSaveUIToParmsAndFile = False

	def makeFramesDataDir(self, fr=None, doMake=True):
		if not fr:
			fr = self.parmDic("fr")
		frameDir = self.framesDataDir + ("/%05d" % fr)
		if doMake:
			ut.mkDirSafe(frameDir)
		return fr, frameDir

	def getSeqVersions(self, verType):
		verDir = self.seqDataDir if verType == "data" else self.seqRenDir
#		vers = [f for f in os.listdir(verDir) if re.match('v[0-9][0-9][0-9]*', f)]
#		vers.sort()
#		vers.reverse()
#
#		# Make v000 dir if there is none.
#		if vers == []:
#			ut.mkDirSafe(verDir + "/v000")
#			vers = ["v000"]
#
		return ut.getVersions(verDir)


	def updateRenAndDataDirs(self):
		# TODO possibly only needed when changing img.
		ut.printFrameStack()

		seqDataDirOLD = self.seqDataDir
		seqDataVDirOLD = self.seqDataVDir
		seqRenDirOLD = self.seqRenDir
		seqRenVDirOLD = self.seqRenVDir

		self.seqDataDir = ut.dataDir + "/" + self.parmDic("image")
		ut.mkDirSafe(self.seqDataDir)
		self.seqDataVDir = self.seqDataDir + "/" + self.parmDic("dataVer")
		self.framesDataDir = self.seqDataVDir + "/frames"

		self.seqRenDir = ut.renDir + "/" + self.parmDic("image")
		ut.mkDirSafe(self.seqRenDir)
		self.seqRenVDir = self.seqRenDir + "/" + self.parmDic("renVer")

		print "\n\n_updateRenAndDataDirs():"
		print "\tself.seqDataDir:", self.seqDataDir,
		if seqDataDirOLD == self.seqDataDir: print
		else: print "-- CHANGED FROM", seqDataDirOLD

		print "\tself.seqDataVDir:", self.seqDataVDir,
		if seqDataVDirOLD == self.seqDataVDir: print
		else: print "-- CHANGED FROM", seqDataVDirOLD

		print "\tself.seqRenDir:", self.seqRenDir,
		if seqRenDirOLD == self.seqRenDir: print
		else: print "-- CHANGED FROM", seqRenDirOLD

		print "\tself.seqRenVDir:", self.seqRenVDir,
		if seqRenVDirOLD == self.seqRenVDir: print
		else: print "-- CHANGED FROM", seqRenVDirOLD
		print

	def getDebugDirAndImg(self, AOVname, lev, sfx=""):
		renAovs = ["bg", "rip", "bg_ctest", "rip_ctest"]
		fr = self.parmDic("fr")
		aovNameWSfx = AOVname + sfx
		if AOVname in renAovs:
			levDir = self.seqRenVDir + "/aov/" + aovNameWSfx
		else:
			levDir = self.seqDataVDir + "/debugImg/" + aovNameWSfx
	
		preFfStr = ""
		if not lev == -1:
			levDir += "/" + lev
			preFfStr = "." + lev 

		imgPath = levDir + ("/" + aovNameWSfx + preFfStr + (".%05d" + self.seqImgExt) % fr)
		return levDir,imgPath

	def getRenDirAndImgPath(self, outputName, lev=None):
		fr = self.parmDic("fr")
		if lev == None:
			levDir = self.seqRenVDir + "/" + outputName
			imgPath = levDir + ("/" + outputName + (".%05d" + self.seqImgExt) % fr)
		else:
			levDir = self.seqRenVDir + "/" + outputName + "/" + lev
			imgPath = levDir + ("/" + outputName + "." + lev +
				(".%05d" + self.seqImgExt) % fr)
		return levDir, imgPath

	def loadImgAndSetRes(self, path, setRes=False, big=False):
		#ut.printFrameStack()
		print "_loadImgAndSetRes(): Attempting to load", path, "...",
		if os.path.exists(path):
			loadedImg = Image.open(path)
			res = loadedImg.size
			if setRes:
				self.res = (res[0]-1, res[1]-1)
			maxResMult = .38 if big else .28
			maxXres = int(maxResMult*self.root.winfo_screenwidth())
			maxYres = int(maxResMult*self.root.winfo_screenheight())
			if res[0] > maxXres or self.displayNaturalRes == 0:
				y = int(res[1] * float(maxXres)/res[0])
				x = maxXres
				if x > maxXres:
					x = int(x*float(maxYres)/y)
					y = maxYres
				res = (x, y)
			self.displayRes = res
			self.reloadErrorImg()
			loadedImg = loadedImg.resize((res[0], res[1]))
			img = ImageTk.PhotoImage(loadedImg)
			print "_loadImgAndSetRes(): success!"
		else:
			img = self.staticImages["error"]
			print "_loadImgAndSetRes(): ********** FAIL! **********"
		return img

	def getOfs(self, fr=None):
		if fr == None:
			fr = self.parmDic("fr")
		return fr/float(self.parmDic("frPerCycle"))

	def getOfsWLev(self, lev, fr=None):
		ofsWLev = self.getOfs(fr) + float(lev)/self.parmDic("nLevels")
		# For interweaving
		return ofsWLev + (lev % 2) * .5

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
			if not self.rootDestroyed:
				Tk.update_idletasks(self.root)

	def addToRenQButCmd(self):
		ut.printFrameStack()
		chosenImg = self.imgChooserVar.get()
		print "\n\n_addToRenQButCmd(): chosenImg:", chosenImg
		self.renQListbox.insert(END, chosenImg)
		self.renQLs = self.renQListbox.get(0, END)
		print "_addToRenQButCmd(): self.renQLs:", self.renQLs

	def rmFromRenQButCmd(self):
		ut.printFrameStack()
		curSelInt = self.renQListbox.curselection()
		curSelStr = None if curSelInt == "" else self.renQListbox.get(curSelInt)
		print "\n\n_rmFromRenQButCmd(): deleting curSelStr:", curSelStr
		self.renQListbox.delete(curSelInt)


	def sortStats(self):
		if self.writeTimerStats:
			print "\n\n_sortStats(): BEGIN\n"
			ut.timerStart(self, "sortStats")
			if self.parmDic("doRenCv") == 1:
				destDir = self.seqRenVDir 
			else:
				destDir = self.seqDataVDir
			srcPath = destDir + "/statsPrintout"
			destPath = destDir + "/statsSummary"

			statsDic = {}
			with open(srcPath) as f:
				for line in f.readlines():
					line = line.strip()
					label, secs = line.split(" ")
					if label == "totalTimeOfAnim":
						continue
					if label in statsDic.keys():
						statsDic[label]["vals"].append(float(secs))
					else:
						statsDic[label]= {"vals":[float(secs)]}

			if len(statsDic.keys()) > 0:
				sortBy = "avg"
				toSort = []
				for label,data in statsDic.items():
					data["total"] = sum(data["vals"])
					data["avg"] = data["total"]/len(data["vals"])
					toSort.append((data[sortBy], label))


				toSort.sort()
				toSort.reverse()
				dud,sortedLables = zip(*toSort)

				print "_sortStats(): writing stats to", destPath + ":"
				if os.path.exists(destPath):
					# open(destPath, 'w') says "file not found" for some reason, so rm first.
					ut.safeRemove(destPath)
					mode = 'w'
				else:
					mode = 'a'
				with open(destPath, mode) as f:
					#f.write("sorted by " + sortBy + ":\n\n")
					for label in sortedLables:
						toWrite = label + " " + str(statsDic[label][sortBy])
						print "_sortStats():\t", toWrite
						f.write(toWrite + "\n")

			print "\n_sortStats(): END\n\n"
			ut.timerStop(self, "sortStats")

	def turnAnimOff(self):
		self.setVal("anim", 0)
		self.sortStats()
		self.recButCmd(False)


	def setupResumeMode(self):
		print "_setupResumeMode(): BEGIN"
		picklingIndicators = glob.glob(self.seqDataVDir + "/pickleInProgress_*")
		if len(picklingIndicators) > 0:
			# Pickling failed; rewind to prev checkpoint after backing up frames.
			picklingIndicatorPath = picklingIndicators[-1]
			print "_setupResumeMode(): picklingIndicatorPath =", picklingIndicatorPath
			# TODO: I think picklingIndicatorPath stuff could all be skipped,
			# simply pickleFailFrame = fr (from last crash)
			pickleFailFrame = int(picklingIndicatorPath[-5:])
			c = self.parmDic("backupDataEvery")
			lastGoodPickleFr = c*((pickleFailFrame - 1)/c)
			print "_setupResumeMode(): lastGoodPickleFr =", lastGoodPickleFr
			framesDir = self.seqDataVDir + "/frames"
			lastGoodDicPath = framesDir + ("/%05d/tidToSids"
				% lastGoodPickleFr)
			print "_setupResumeMode(): lastGoodDicPath =", lastGoodDicPath
			if os.path.exists(lastGoodDicPath):
				print "_setupResumeMode(): Exists!  Backing up junk frames..."
				timeSfx = time.strftime("%m_%d_%H_%M", time.gmtime())
				bakDir = framesDir + "/bak_" + timeSfx
				for ffr in range(lastGoodPickleFr+1, pickleFailFrame+1):
					base = ("/%05d" % ffr)
					src = framesDir + base
					print "_setupResumeMode(): Moving", src, "to", bakDir + base
					shutil.move(src, bakDir + base)

				print "_setupResumeMode(): Setting fr =", \
					lastGoodPickleFr, "anim = 1, record = True"
				self.setVal("fr", lastGoodPickleFr + 1)
				self.setVal("anim", 1)
				self.record = True
			else:
				print "_setupResumeMode(): Doesn't exist!  Uh oh..."
		
		else:
			# Some non-pickle crash eg. GPU; resume from this fr.
			self.setVal("anim", 1)
			self.record = True

	def makeCInOutValsLs(self):
		cInOutNameVals = []
		RGBto012 = {"R":"0R", "G":"1G", "B":"2B"}
		for pmName,v in self.parmDic.parmDic.items():
			if pmName[:3] == "cIn" or pmName[:4] == "cOut":
				pmNameMod = pmName[:-1] + RGBto012[pmName[-1]]
				cInOutNameVals.append((pmNameMod, v))

		cInOutNameVals.sort()
		self.cInOutVals = []

		for i in cInOutNameVals:
			for ss in i[1]["val"].split(","):
				self.cInOutVals.append(float(ss))


	def setFillMode(self):
		#self.fillMode = "overwrite"
		# if self.parmDic("frIncRen") == 0: TEMP no overwrite for final render!
		# 	self.fillMode = "fill"
		# elif self.parmDic("frIncRen") < 0:
		# 	self.fillMode = "onlyBg"
		self.fillMode = "fill"

	def getRenderedAovNames(self):
		# Debug images.
		path = self.seqDataVDir + "/debugImg"
		sourceImagesGen = []
		if os.path.exists(path):
			sourceImagesGen = os.listdir(path)
			sourceImagesGen.sort()
		print "\n\n\n XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
		print "_getRenderedAovNames(): images loaded from", path + ":", sourceImagesGen

		path = self.seqRenVDir + "/aov"
		sourceImagesRen = []
		if os.path.exists(path):
			sourceImagesRen = os.listdir(path)
			sourceImagesRen.sort()
		print "_getRenderedAovNames(): images loaded from", path + ":", sourceImagesRen

		sourceImages = sourceImagesGen + sourceImagesRen

		print "_getRenderedAovNames(): all images loaded:", sourceImages

		if sourceImages == []:
			sourceImages = ["----"]

		return sourceImages

	def updateRenderedAovMenu(self, opMenu, col, aovName):
		varName = StringVar(self.frameParm)
		varName.set(self.parmDic.parmDic[aovName]["val"])
		opMenu['menu'].delete(0, 'end')
		aovNames = self.getRenderedAovNames()
		for aovName in aovNames:
			#imgChooser['menu'].add_command(0, 'end')
			opMenu['menu'].add_command(label=aovName,
				command=self.getImgDebugFunctions["name"][col])
	def updateBreaths(self):
		print "_updateBreaths()"
		self.inhParms = []
		self.exhParms = []
		for pd in self.parmDic.parmDic.items():
			parmName = pd[0]
			if not parmName[-4:] == "trip":
				if parmName[:3] == "inh":
					self.inhParms.append((parmName, int(pd[1]["val"])))
				elif parmName[:3] == "exh":
					self.exhParms.append((parmName, int(pd[1]["val"])))
		
		self.inhParms.sort()
		self.exhParms.sort()
		self.breathsNameFrTrip = []
		for i in range(len(self.inhParms)):
			inhTripVal = self.parmDic(self.inhParms[i][0] + "trip")
			self.breathsNameFrTrip.append(self.inhParms[i] + (inhTripVal,))
			exhTripVal = self.parmDic(self.exhParms[i][0] + "trip")
			self.breathsNameFrTrip.append(self.exhParms[i] + (exhTripVal,))


	def __init__(self, resumeMode=False):
		print "_warpUi.__init__(): resumeMode =", resumeMode

		# Not currently dirty
		dirtyIndicator = ut.projDir + "/dirty"
		ut.safeRemove(dirtyIndicator)

		# TODO: Organize all this crap.
		# Needed for pickling.
		lim = sys.getrecursionlimit()
		sys.setrecursionlimit(lim*1000)
		self.seqImgExt = ".png"
		
		self.getImgDebugFunctions = {
				"name":[self.getImgDebug1, self.getImgDebug2],
				"lev":[self.getLevDebug1, self.getLevDebug2]
		}

		# THIS IS WHERE PARMS ARE INITIALLY LOADED
		self.parmDic = ut.parmDic(parmPath)
		self.makeCInOutValsLs()

		self.updateBreaths()


		print "_warpUi.__init__(): self.breathsNameFrTrip", self.breathsNameFrTrip

		#print "\n\n\n__init__():********** parmDic"
		#print self.parmDic
		self.pauseSaveUIToParmsAndFile = False
		self.parmEntries = {}
		self.renQLs = []
		self.displayRes = (1, 1)
		self.seqDataDir = ut.dataDir + "/" + self.parmDic("image")
		self.seqDataVDir = self.seqDataDir + "/" + self.parmDic("dataVer")
		self.seqRenDir = ut.renDir + "/" + self.parmDic("image")
		self.seqRenVDir = self.seqRenDir + "/" + self.parmDic("renVer")

		# Init opencl stuff.
		ut.indicateProjDirtyAs(self, True, "createContextAndQueue_inProgress")
		print "_warpUi.__init__(): before _create_some_context()"
		self.cntxt = cl.create_some_context()
		print "_warpUi.__init__(): after _create_some_context(); before _CommandQueue"
		self.queue = cl.CommandQueue(self.cntxt)
		print "_warpUi.__init__(): after _CommandQueue"
		ut.indicateProjDirtyAs(self, False, "createContextAndQueue_inProgress")



		self.timerStarts = {}
		self.writeTimerStats = False
		global statsDirDest # for cProfile
		statsDirDest = self.seqRenVDir 
		self.inSurfGridPrev = None
		self.tidPosGrid = None
		self.spritesThisFr = None
		self.spritesLoadedFr = None
		#self.srcImg = None
		self.sidToCvDic = None
		#self.tholds = None
		self.dataLoadedForFr = -1
		self.setVal("anim", 0)
		self.updateRenAndDataDirs()
		self.nextSid = 0
		self.tidToSids = None
		#self.sidToTid = None
		self.tholds = None
		self.root = Tk()
		self.root.wm_title("WARP")
		self.rootDestroyed = False
		self.positionWindow()
		self.gridJt = None
		self.gridLevels = None
		self.record = False
		self.seqEnd = -100
		self.seqStart = 10000000
		self.frStartAnim = 0
		self.timeStart = time.time()
		self.animFrStart = self.parmDic("fr")
		self.chkVars = {}
		self.displayNaturalRes = 0
		self.genRen1fr = 0

		if resumeMode:
			self.setupResumeMode()


		# TODO e needed?
		self.root.bind('<Return>', lambda e: self.returnCmd())
		self.root.bind('<Control-Return>', lambda e: self.ctlReturnCmd())
		self.root.bind('<Shift-Return>', lambda e: self.shiftReturnCmd())
		self.root.bind('<Control-Shift-Return>', lambda e: self.rebuildUI())
		#self.root.bind('<KeyPress>', self.keyPress)
		for kk in ["Left", "Right", "Escape", "Control-Left", "Control-Right", "space", "c", "r", "x", "g"]:
			self.root.bind('<' + kk + '>', self.execHotkey)
		self.root.bind('<Control-Left>', lambda e: self.rewButCmd())
		self.root.bind('<Control-Right>', lambda e: self.ffwButCmd())
		self.root.bind('<Shift-Right>', lambda e: self.shiftRightCmd())
		self.root.bind('<Shift-Left>', lambda e: self.shiftLeftCmd())
		self.root.bind('<Alt-Return>', lambda e: self.imgButCmd())

		#self.root.bind('<Control-Left>', lambda e: self.rewButCmd())
		# Load images.
		self.staticImageNames = ["play", "pause", "rew", "stepBack", "stepFwd", "ffw", "recOn", "recOff", "error"]
		self.varyingStaticImageNames = ["anim", "rec"]
		self.staticImages = {}
		base = ut.imgDir + "/controls/"
		self.errorImgPath = base + "error" + ut.statImgExt
		for name in self.staticImageNames:
			loadedImg = Image.open(base + name + ut.statImgExt)
			print "_warpUi.__init__(): name:" + name + "; loadedImg", loadedImg
			#res = loadedImg.size
			self.staticImages[name] = ImageTk.PhotoImage(loadedImg)
		self.images = {}
		res = self.loadImages()

		# AOVs.
		self.aovNames = []
		for parmName in self.parmDic.parmDic.keys():
			if parmName[:4] == "aov_" and self.parmDic(parmName) == 1:
				self.aovNames.append(parmName[4:])

		nLevels = self.parmDic("nLevels")
		self.aovDic = {}
		for aovName in self.aovNames:
			# The last cell - that is, [nLevels] - is reserved for "all"
			self.aovDic[aovName] = [pygame.Surface(res) for i in range(nLevels+1)][:]



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


		# Natural res checkbox
		self.chk_genRen1fr_var = IntVar()
		self.chk_genRen1fr_var.set(self.displayNaturalRes)
		self.chk_genRen1fr = Checkbutton(self.frameTopControls,
			text="Gen Ren 1 fr", variable=self.chk_genRen1fr_var,
			command=self.chk_genRen1fr_cmd)
		self.chk_genRen1fr.grid(row=row, column=0, sticky=W)


		# Natural res checkbox
		self.chk_naturalRes_var = IntVar()
		self.chk_naturalRes_var.set(self.displayNaturalRes)
		self.chk_naturalRes = Checkbutton(self.frameTopControls,
			text="Natural Res", variable=self.chk_naturalRes_var,
			command=self.chk_naturalRes_cmd)
		self.chk_naturalRes.grid(row=row, column=1, sticky=W)


		# Do renCv checkbox
		self.chk_doRenCv_var = IntVar()
		self.chk_doRenCv_var.set(self.parmDic("doRenCv"))
		self.chk_doRenCv = Checkbutton(self.frameTopControls, text="Ren Mode", variable=self.chk_doRenCv_var, command=self.chk_doRenCv_cmd)
		self.setRenCvUIClr()
		self.chk_doRenCv.grid(row=row, column=2, sticky=W)
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

		# Version choosers

		self.verTypeLs = ["data", "ren"]
		self.verUI = {}
		# Example:
		# {'data': {'OptionMenu': <Tkinter.OptionMenu instance at 0x7fbd2e0f3680>,
		#	   'menuVar': <Tkinter.StringVar instance at 0x7fbd2e0f3290>,
		#	   'sfx': <Tkinter.Entry instance at 0x7fbd2e0fd248>},
		#  'ren': {'OptionMenu': <Tkinter.OptionMenu instance at 0x7fbd2e0fd3b0>,
		#	   'menuVar': <Tkinter.StringVar instance at 0x7fbd2e0fd320>,
		#	   'sfx': <Tkinter.Entry instance at 0x7fbd2e0fdd40>}}


		#for verType in self.verUI.keys():
		self.verFrame = Frame(self.frameParmAndControls)
		self.verFrame.grid(row=row)
		row += 1
		verRow = 0
		for verType in self.verTypeLs:
			self.verUI[verType] = {}
			verLabel = Label(self.verFrame, text=(verType + "Version"))
			verLabel.grid(row=verRow, column=0, sticky=E)


			frameImgVmenu = Frame(self.verFrame)
			frameImgVmenu.grid(row=verRow, column=1, sticky=EW)
			verRow += 1
			#frameImgVnew = Frame(self.verFrame)
			#frameImgVnew.grid(row=verRow, column=1, sticky=EW)

			self.verUI[verType]["menuVar"] = StringVar(frameImgVmenu)
			self.verUI[verType]["menuVar"].set(self.parmDic(verType + "Ver"))
			print "_warpUi.__init__(): --- self.verUI[verType][\"menuVar\"].get()", self.verUI[verType]["menuVar"].get()
			vers = self.getSeqVersions(verType)
			print "\n__init__(): " + verType + " vers:", vers

			print "\n\n__init__(): setting up OptionMenu for", verType
			self.verUI[verType]["OptionMenu"] = OptionMenu(frameImgVmenu, self.verUI[verType]["menuVar"], *vers, command=lambda selection, thisVerType=verType : self.menuVChooser(selection, thisVerType))
			self.verUI[verType]["OptionMenu"].grid(row=verRow, column=0, sticky=EW)

			self.verUI[verType]["sfx"] = Entry(self.verFrame, width=22)
			self.verUI[verType]["sfx"].grid(row=verRow, column=1, sticky=W)

			verButton = Button(self.verFrame, text="Make New", command=lambda thisVerType=verType : self.butVNew(thisVerType))
			verButton.grid(row=verRow, column=0, sticky=W)

			verRow +=1

			# Add entry to dic of corresponding types.
			# TODO: maybe make this if/else thing into a function for initiating/appending lists
			if "str" in self.parmEntries.keys():
				self.parmEntries["str"].append(self.verUI[verType]["sfx"])
			else:
				self.parmEntries["str"] = [self.verUI[verType]["sfx"]]

			#self.imgVNewLabel.grid(row=0, column=1)
			verRow += 1


		# Render queue controls - TODO: collapsible, better layout (stack buttons + label)
		frameRenQueue = Frame(self.frameParmAndControls)
		frameRenQueue.grid(row=row, sticky=S) # Not convinced sticky does anything here.

		if False: # No queue for now...
			thisLabel = Label(frameRenQueue, text="RenQ", justify="left")
			thisLabel.grid(row=row, column=0)

			thisButton = Button(frameRenQueue, text="+", command=lambda:self.addToRenQButCmd())
			thisButton.grid(row=row, column=1)

			thisButton = Button(frameRenQueue, text="-", command=lambda:self.rmFromRenQButCmd())
			thisButton.grid(row=row, column=2)

			self.renQListbox = Listbox(frameRenQueue, height=4)
			self.renQListbox.grid(row=row, column=3)

		#for item in ["one", "two", "three", "four", "fv", "sx", "sv"]:
		#	self.renQListbox.insert(END, item)


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


		frameRen = Frame(self.frameImg)
		thisLabel = Label(frameRen, text="ren")
		thisLabel.grid(row=0)
		thisButton = self.makeImgButton("ren", frameRen)
		thisButton.grid(row=1)
		frameRen.grid(row=0)

		frameSrc = Frame(self.frameImg)
		thisLabel = Label(frameSrc, text="source")
		thisLabel.grid(row=1)
		thisButton = self.makeImgButton("source", frameSrc)
		thisButton.grid(row=0)
		frameSrc.grid(row=1)



		sourceImages = self.getRenderedAovNames()

		self.dbMenus = {}
		col = 0

		aovParmNames = self.getDbImgParmNames()
		aovNum = 0
		for aovName in aovParmNames:
			print "_warpUi.__init__(): \\\\\\\\\\\\ col", col, "aovName", aovName
			frameDbParm = Frame(self.frameImg)
			thisButton = self.makeImgButton(aovName, frameDbParm)
			thisButton.grid(row=(1-aovNum))
			
			frameDbMenus = Frame(frameDbParm)
			frameDbMenus.grid(row=aovNum)
			varName = StringVar(self.frameParm)
			# TODO: Replace with parmDic(aovName) -- look for other instances that need similar replacement.
			varName.set(self.parmDic.parmDic[aovName]["val"])
			imgChooser = OptionMenu(frameDbMenus, varName, *sourceImages, command=self.getImgDebugFunctions["name"][col])

			#self.updateRenderedAovMenu(imgChooser, col, aovName)
			imgChooser.grid()

			varLev = StringVar(self.frameParm)
			varLev.set(self.parmDic("lev_" + aovName))
			levs = ["lev%02d" % i for i in range(self.parmDic("nLevels"))] + ["ALL"]
			levChooser = OptionMenu(frameDbMenus, varLev, *levs,
				command=self.getImgDebugFunctions["lev"][col])
			levChooser.grid(row=0,column=1)

			# TODO: varName and varLev are not yet used.
			self.dbMenus[aovName] = {"menu":imgChooser,
				"varName":varLev, "varLev":varLev}
			frameDbParm.grid(row=aovNum,column=1)
			aovNum += 1


		# Update menu-dependent images to reflect current selection.
		print "\n__init__():  ****** doing self._getImg", self.parmDic("image")
		self.getImg(self.parmDic("image")) 
		while not self.rootDestroyed:
			anim = self.parmDic("anim")
			if anim == 1:
				nLevels = self.parmDic("nLevels")
				frStart = self.parmDic("frStart")
				frEnd = self.parmDic("frEnd")
				fr = self.parmDic("fr")
				frPerCycle = self.parmDic("frPerCycle")
				secondsPassed = time.time() - self.timeStart

				newFr = self.frStartAnim + int(secondsPassed*self.parmDic("fps"))
				if newFr > fr:		
					inc = 1 if self.parmDic("frIncRen") <= 0 else self.parmDic("frIncRen")
					fr = min(fr + inc, newFr)
					framesPassed = fr - self.frStartAnim
					secPerFr = 0 if framesPassed == 0 else secondsPassed/framesPassed
					framesToGo = self.parmDic("frEnd") - fr
					secondsToGo = secPerFr * framesToGo

					hmsPerFr = ut.secsToHms(secPerFr)
					hmsPassed = ut.secsToHms(secondsPassed)
					hmsToGo = ut.secsToHms(secondsToGo)
					eta = datetime.datetime.now() + datetime.timedelta(seconds=secondsToGo)


					statsMsg =  """


%%%%%%%%%%%%%%%%%%%%%%% TIME STATS %%%%%%%%%%%%%%%%%%%%%%%
% fr: """ + str(fr) + " (" + str(fr - frStart + 1) + " of " + str(frEnd - frStart + 1) + """)
% animFrStart: """ + str(self.animFrStart) + """
% frames passed in this anim: """ + str(framesPassed) + """
% Time passed in this anim: """ + str(hmsPassed) + " (" + str(secondsPassed) + """ seconds)
% Avg time per fr: """ + str(hmsPerFr) + " (" + str(secPerFr) + """ seconds)
% Est time left in this anim: """ + str(hmsToGo) + " (" + str(secondsToGo) + """ seconds)
%
% ETA""" + str(eta) + """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



"""

					print "_warpUi.__init__(): statsMsg:", statsMsg
					with open(self.seqRenVDir + "/stats", 'w') as f:
						f.write(statsMsg)


					frEnd = self.parmDic("frEnd")
					if fr > frEnd:
						# What to do when you've reached end of seq.
						if self.record:
							# Global varable needed for final stats
							statsDirDest = self.seqRenVDir 

							doRenCv = self.parmDic("doRenCv")
							frIncRen = self.parmDic("frIncRen")
							if doRenCv == 0 and frIncRen == 0:
								self.setVal("fr", frEnd)
								# Back up tidToSids for final frame, if not already done.
								if not frEnd % self.parmDic("backupDataEvery") == 0:
									print "_warpUi.__init__(): BACKING UP tidToSids for final fr", fr
									genData.saveTidToSid(self)

							# TODO: rename - for now doRenCv=currently doing ren; doRen=you should do ren
							if (doRenCv==0 and self.parmDic("doRen")==1) or \
								(doRenCv==1 and self.parmDic("doRen")==1
									and (not frIncRen == 0)):
								# You're set to do render, but doRenCv=0 (not yet done),
								# or you haven't filled the seq yet (frIncRen != 0)

								# Write stats
								secondsPassed = time.time() - self.timeStart
								hmsPassed = ut.secsToHms(secondsPassed)
								ut.writeTime(self, "totalTimeOfAnim", hmsPassed)

								print "_warpUi.__init__(): Turning on doRenCv"
								if doRenCv==0: # ren not done; set doRenCv on
									self.setVal("doRenCv", 1)
								else: # frIncRen > 1; set to 0 for fill mode.
									self.setVal("frIncRen", 0)
								self.chk_doRenCv_var.set(1)
								self.setRenCvUIClr()
								print "_warpUi.__init__(): Returning to", self.parmDic("frStart")
								# Restart
								fr = self.parmDic("frStart")
							elif self.parmDic("image") in self.renQLs and not self.parmDic("image") == self.renQLs[-1]:
								# If recording and in renQ but not last,
								# turn off doRenCv, restart, and go to next img.
								# TODO: Make stats work for multiple seq
								nextImg = self.renQLs[self.renQLs.index(self.parmDic("image")) + 1]
								self.setVal("image", nextImg)
								self.imgChooserVar.set(nextImg)
								self.menuImgChooser(nextImg)
								# record should always be False after menuImgChooser, but throw in "if" just in case.
								if not self.record: self.recButCmd() 
								if self.parmDic("doGen") == 1:
									self.setVal("doRenCv", 0)
									self.chk_doRenCv_var.set(0)
								fr = self.parmDic("frStart")
							else:
								# If recording and not - or last - in renQ, stop.
								self.recButCmd()
								fr -= 1
								self.turnAnimOff()
								secondsPassed = time.time() - self.timeStart
								hmsPassed = ut.secsToHms(secondsPassed)
								ut.writeTime(self, "totalTimeOfAnim", hmsPassed)
						else:
							# Loop if not recording
							print "_warpUi.__init__(): Returning to", self.parmDic("frStart")
							fr = self.parmDic("frStart")
							self.timeStart = time.time()
							#self.animFrStart = fr

					# This forces each fr to process, ie. ACTUALLY GENERATES THE DATA.
					# TODO: maybe add forceFps
					self.setFrAndUpdate(fr)

				self.setVal("fr", fr)
			if not self.rootDestroyed:
				Tk.update_idletasks(self.root)
				Tk.update(self.root)


profiling = False

resumeMode = False
if len(sys.argv) > 1 and sys.argv[1] == "-r":
	resumeMode = True


if profiling:
	cProfile.run('warpUi()', statsObjPathSrc)
	shutil.copy2(statsObjPathSrc, statsDirDest)
else:
	warpUi(resumeMode=resumeMode)
	sys.exit()
#with open(path, 'w') as f:
