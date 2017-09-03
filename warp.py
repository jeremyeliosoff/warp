#!/usr/bin/python
import os, genData, ut, time, datetime, pprint, glob, cProfile
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
		ut.exeCmd("killall warp.py; /home/jeremy/dev/warp/warp.py")
		
	def saveDics(self):
		print "\n_saveDics(): Saving dics..."
		genData.pickleDump(self.seqDataVDir + "/tidToSids", self.tidToSids)
		genData.pickleDump(self.seqDataVDir + "/sidToTid", self.sidToTid)

	def delDics(self):
		print "\n_delDics(): Deleting dics..."
		ut.exeCmd("rm " + self.seqDataVDir + "/tidToSids")
		ut.exeCmd("rm " + self.seqDataVDir + "/sidToTid")
		
	def flushDics(self):
		print "\n_flushDics(): Flushing dics"
		self.tidToSids = None
		self.sidToTid = None
		self.nextSid = 0
		
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
		print "\n_saveUIToParmsAndFile(): self.pauseSaveUIToParmsAndFile =", self.pauseSaveUIToParmsAndFile
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
					print "_saveUIToParmsAndFile(): v", v
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
	
	def makeParmUi(self, startRow):
		row = startRow
		self.nbExclude = ttk.Frame(self.frameParmAndControls)
		self.nbExclude.grid(row=1)
		self.nbParm = ttk.Notebook(self.frameParmAndControls)
		self.nbParm.grid(row=2)
		self.nbFrames = {}
		#stages = self.parmDic.parmStages.keys()
		#stages.sort() # Just to get GEN in front of REN
		#TODO make this dynamically depend on parms file
		stages = ["META", "GEN", "REN", "AOV"]
		for stage in stages:
			if not stage == "META":
				self.nbFrames[stage] = ttk.Frame(self.nbParm)
				self.nbParm.add(self.nbFrames[stage], text=stage)
		for parmName,dic in self.parmDic.parmLs: # Recall: parmLs = [("parmName", {'key':val...}]
			thisParmDic = self.parmDic.parmDic[parmName]
			print "_makeParmUi(): parmName:", parmName, ", thisParmDic:", thisParmDic
			
			if "hidden" in thisParmDic.keys() and thisParmDic["hidden"] == "True":
				print "_makeParmUi(): HIDDEN, skipping..."
				continue

			#for stage,parmNames in self.parmDic.parmStages.items():
			#	if stage == "META":
			#		thisFrame = self.nbExclude
			#	elif parmName in parmNames:
			#		thisFrame = self.nbFrames[stage]
			#lab = Label(self.frameParm, text=parmName)
			thisStage = thisParmDic["stage"]
			print "_makeParmUi(): \t thisStage:", thisStage
			if thisStage == "META":
				thisFrame = self.nbExclude
			else:
				thisFrame = self.nbFrames[thisStage]

			lab = Label(thisFrame, text=parmName)
			lab.grid(row=row, column=0, sticky=E)


			if thisParmDic["type"] == "clr":
				clrTuple = self.parmDic(parmName)
				hx = ut.rgb_to_hex(clrTuple)
				#ent = Button(self.frameParm, width=10, bg=hx,command=lambda args=(parmName,clrTuple): self.btn_getColor(args))
				ent = Button(thisFrame, width=10, bg=hx,command=lambda args=(parmName,clrTuple): self.btn_getColor(args))
			elif thisParmDic["type"] == "bool":
				self.chkVars[parmName] = IntVar()
				self.chkVars[parmName].set(self.parmDic(parmName))
				ent = Checkbutton(thisFrame, variable=self.chkVars[parmName], command=lambda pn=parmName: self.chk_cmd(pn))
		#self.chk_doRenCv = Checkbutton(self.frameTopControls, text="Do renCv", variable=self.chk_doRenCv_var, command=self.chk_doRenCv_cmd)
			else:
				#ent = Entry(self.frameParm)
				ent = Entry(thisFrame)
			ent.grid(row=row, column=1, sticky=W)
			thisParmDic["uiElement"] = ent

			# Add entry to dic of corresponding types.
			if thisParmDic["type"] in self.parmEntries.keys():
				self.parmEntries[thisParmDic["type"]].append(ent)
			else:
				self.parmEntries[thisParmDic["type"]] = [ent]

			if not thisParmDic["type"] in ["clr", "bool"]:
				sv = StringVar()
				sv.trace("w", lambda name, index, mode, sv=sv, pn=parmName: self.saveUIToParmsAndFile(pn, sv))

				thisParmDic["uiElement"].configure(textvariable=sv)
				thisParmDic["uiElement"].insert(0, str(thisParmDic["val"]))

			row += 1
		print "\n\n_makeParmUi(): parmDic"
		for k,v in self.parmDic.parmDic.items():
			print "_makeParmUi(): \t", k, v["val"]
		print "\n\n_makeParmUi(): parmLs:", self.parmDic.parmLs
		return row
		

	def positionWindow(self):
		w = 1500 # width for the Tk root
		h = 950 # height for the Tk root

		# get screen width and height
		ws = self.root.winfo_screenwidth() # width of the screen
		hs = self.root.winfo_screenheight() # height of the screen

		# calculate x and y coordinates for the Tk root window
		x = ws/8
		y = hs/12
		#x = ws - (w/2)
		#y = hs - (h/2)

		# set the dimensions of the screen 
		# and where it is placed
		self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))


	def getDbImgParmNames(self):
		dbImgNames = []
		root = "dbImg"
		for k in self.parmDic.parmDic.keys():
			if k[:len(root)] == root:
				dbImgNames.append(k)
		print "\n_getDbImgParmNames() dbImgNames:", dbImgNames
		dbImgNames.sort()
		return dbImgNames
	
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
		#self.images["rew"] = {"path":self.images["rew"]["path"]}

		print "_loadImages(): images:"
		for i,k in self.images.items():
			print i, k

		for img in self.images.keys():
			if not img in (self.staticImageNames + self.varyingStaticImageNames):
				path = self.images[img]["path"]
				print "_loadImages(): Checking existence of", path
				self.images[img]["pImg"] = self.loadImgAndSetRes(path)

		image = self.images["source"]["pImg"]
		#self.res = (image.width(), image.height())
		
		self.reloadErrorImg()

	def refreshPhotoImages(self):
		# TODO you shouldn't have to reload ALL images eg. play, pause - maybe
		# keep those images "on hand" as PhotoImages that you switch between
		for k,thisDic in self.images.items():
			if not k in (self.staticImageNames + self.varyingStaticImageNames):
				pImg = self.loadImgAndSetRes(thisDic["path"])
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

		for butName,butDic in self.images.items():
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
		self.updateCurImg(forceRecord=True)
		self.updateDebugImg()

	def keyPress(self, event):
		print "_keyPress(): event.keysym", event.keysym
		focused = self.frameMaster.focus_get()
		dataType = None
		for typ,ents in self.parmEntries.items():
			if focused in ents:
				print "_keyPress(): \tdata typ:", typ
				dataType = typ
				break


	def setFrAndUpdate(self, fr):
		self.setStatus("busy")
		self.setVal("fr", fr)
		self.saveParmDic()
		self.updateRenAndDataDirs()
		self.updateCurImg()
		self.updateDebugImg()
		Tk.update_idletasks(self.root)
		

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
			elif key == "x":
				self.imgButCmd()

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
			# If you're animating and recording and doGen == 0, turn on doRenCv
			if self.record and self.parmDic("doGen") == 0:
				self.setVal("doRenCv", 1)
				self.chk_doRenCv_var.set(1)

			self.refreshButtonImages()
			self.timeStart = time.time()
			self.frStartAnim = self.parmDic("fr")
			self.updateCurImg()
		else:
			self.turnAnimOff()
			self.refreshButtonImages()
		print "_animButCmd(): Pressed anim button, anim set to", anim

	def recButCmd(self, val=None):
		if val == None:
			self.record = not self.record
		else:
			self.record = val
		print "_recButCmd(): self.record =", self.record
		self.refreshButtonImages()

	def toggleDoRenCv(self):
		if self.chk_doRenCv_var.get() == 1:
			val = 0
		else:
			val = 1
		self.chk_doRenCv_var.set(val)
		self.setVal("doRenCv", val)

	def saveParmDic(self):
		print "_saveParmDic(): BEGIN"
		# TODO Maybe don't hardwire this, user can config it in parmfile
		pathsAndStages = [(parmPath, ["META", "GEN", "REN", "AOV"])]
		print "_saveParmDic(): self.seqDataVDir:", self.seqDataVDir, "for GEN -- ",
		# TODO Shouldn't seqDataVDir and seqRenVDir always exist?
		if os.path.exists(self.seqDataVDir):
			pathsAndStages.append((self.seqDataVDir + "/parms", ["GEN"]))
			print "EXISTS"
		else:
			print "DOES NOT EXIST"

		print "_saveParmDic(): self.seqRenVDir:", self.seqRenVDir, "for REN -- ",
		if os.path.exists(self.seqRenVDir):
			pathsAndStages.append((self.seqRenVDir + "/parms", ["META", "REN"]))
			print "EXISTS"
		else:
			print "DOES NOT EXIST"

		print "_saveParmDic(): self.parmDic.parmStages:"
		for k,v in self.parmDic.parmStages.items():
			print "\t", k, ":", v

		print "\n\nsaveParmDic(): parmLs:"
		for pm in self.parmDic.parmLs:
			print pm[0],
		print

		for path, stages in pathsAndStages:
			print "_saveParmDic(): path", path, "stages", stages
			with open(path, 'w') as f:
				for stage in stages:
					f.write("\n\n\n---" + stage + "---\n\n")

					for parm in self.parmDic.parmStages[stage]:
						# fr and image only go in the top level, shared parm file
						if stage == "META" or not parm in ["fr", "image"]:
							f.write(parm + "\n")
							thisDic = self.parmDic.parmDic[parm]
							keys = thisDic.keys()
							keys.sort()
							for attr in keys:
								if not attr in ["uiElement", "stage"]:
									 f.write(attr + " " + str(thisDic[attr]) + "\n")
							f.write("\n")


	def updateDebugImg(self):
		print "\n_updateDebugImg(): BEGIN"
		for i in range(2):
			img = self.parmDic("dbImg" + str(i+1))
			lev = self.parmDic("lev_dbImg" + str(i+1))
			dbImgPath = self.getDebugDirAndImg(img, lev)[1]
			self.images["dbImg" + str(i+1)]["path"] = dbImgPath
			self.setVal("dbImg" + str(i+1), img)
			print "_updateDebugImg(): dbImgPath", dbImgPath
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
		print "_updateCurImg(): self.parmDic(image)", self.parmDic("image")
		self.images["source"]["path"] = self.getSourceImgPath()
		print "_updateCurImg(): self.images[source][path]:", self.images["source"]["path"]
		dud, renImgPath = self.getRenDirAndImgPath("ren", "ALL")

		self.images["ren"]["path"] = renImgPath
		print "\n_updateCurImg(): self.record", self.record

		ut.exeCmd("rm " + genData.outFile)
		genData.pOut("\nPRE genData")

		######## THIS IS WHERE DATA GETS GENERATED ########
		if self.record or forceRecord:
			genData.pOut("doing genData")
			reload(genData)
			self.setStatus("busy", "Doing genData...")
			if self.inSurfGridPrev == None:
				prevFr, prevFrameDir = self.makeFramesDataDir(self.parmDic("fr") - 1)
				prevFrInSurfGrid = prevFrameDir + "/inSurfGrid" 
				if os.path.exists(prevFrInSurfGrid): # pickleLoad already checks this but prints error
					print "\n\n_updateCurImg(): LOADING inSurfGrid from ", prevFrInSurfGrid, "\n"
					self.inSurfGridPrev = genData.pickleLoad(prevFrInSurfGrid)

			ut.timerStart(self, "genData")
			genData.genData(self, self.seqRenVDir)
			ut.timerStop(self, "genData")

			print "\n_updateCurImg(): Done genData\n\n"
			self.setStatus("idle")
		else:
			genData.pOut("skipping genData")
		###################################################
		


		self.refreshButtonImages()
		image = self.images["source"]["pImg"]
		#self.res = (image.width(), image.height())
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
		thisImg = selection
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
			if self.record:
				# Turn off recording so you don't render right away.
				self.recButCmd()
			self.setVal("image", selection) #TODO: Rename image to maybe seqName?
			self.flushDics()
			self.updateRenAndDataDirs()
			self.updateCurImg()
			self.updateDebugImg()

	def repopulateMenu(self, verType, vers):
		menu = self.verUI[verType]["OptionMenu"]["menu"]
		menu.delete(0, "end")
		for s in vers:
			menu.add_command(label=s, command=lambda value=s: self.verUI[verType]["menuVar"].set(value))

	def menuImgChooser(self, selection):
		print "\n_menuImgChooser(): pre getImg"
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
		print "\n_menuImgChooser(): post getImg"
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
		self.flushDics()


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
		ut.exeCmd("cp " + verDir + "/" + latestVer + "/parms " + verDir + "/" + nextVer + "/")
		self.setVal(verType + "Ver", nextVer)

		vers = [nextVer] + vers
		self.repopulateMenu(verType, vers)
		self.verUI[verType]["menuVar"].set(nextVer)
		self.menuVChooser(nextVer, verType)


	# TODO: rename to renMode, make it a case of chk_cmd
	def chk_doRenCv_cmd(self):
		val = self.chk_doRenCv_var.get()
		print "_chk_doRenCv_var(): Setting doRenCv to:", val
		self.setVal("doRenCv", val)
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

	def makeFramesDataDir(self, fr=None):
		if not fr:
			fr = self.parmDic("fr")
		frameDir = self.framesDataDir + ("/%05d" % fr)
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
		ut.printFrameStack()
		print "_updateRenAndDataDirs(): OLD:\n_updateRenAndDataDirs(): \tseqDataDir:", self.seqDataDir, "\n_updateRenAndDataDirs():\tseqDataVDir:", self.seqDataVDir, "\n_updateRenAndDataDirs():\tseqRenDir", self.seqRenDir, "\n_updateRenAndDataDirs():\tseqRenVDir", self.seqRenVDir
		self.seqDataDir = ut.dataDir + "/" + self.parmDic("image")
		ut.mkDirSafe(self.seqDataDir)
		self.seqDataVDir = self.seqDataDir + "/" + self.parmDic("dataVer")
		self.framesDataDir = self.seqDataVDir + "/frames"

		self.seqRenDir = ut.renDir + "/" + self.parmDic("image")
		ut.mkDirSafe(self.seqRenDir)
		self.seqRenVDir = self.seqRenDir + "/" + self.parmDic("renVer")
		print "\n_updateRenAndDataDirs(): NEW:\n_updateRenAndDataDirs():\tseqDataDir:", self.seqDataDir, "\n_updateRenAndDataDirs():\tseqDataVDir:", self.seqDataVDir, "\n_updateRenAndDataDirs():\tseqRenDir", self.seqRenDir, "\n_updateRenAndDataDirs():\tseqRenVDir", self.seqRenVDir

	def getDebugDirAndImg(self, debugInfo, lev):
		fr = self.parmDic("fr")
		levDir = self.seqDataVDir + "/debugImg/" + debugInfo + "/" + lev # TODO: v00
		imgPath = levDir + ("/" + debugInfo + "." + lev + ".%05d.jpg" % fr)
		return levDir,imgPath

	def getRenDirAndImgPath(self, outputName, lev=None):
		fr = self.parmDic("fr")
		if lev == None:
			levDir = self.seqRenVDir + "/" + outputName
			imgPath = levDir + ("/" + outputName + ".%05d.jpg" % fr)
		else:
			levDir = self.seqRenVDir + "/" + outputName + "/" + lev
			imgPath = levDir + ("/" + outputName + "." + lev + ".%05d.jpg" % fr)
		return levDir, imgPath

	def loadImgAndSetRes(self, path):
		#ut.printFrameStack()
		print "_safeLoad(): Attempting to load", path, "...",
		if os.path.exists(path):
			loadedImg = Image.open(path)
			res = loadedImg.size
			self.res = res
			sc = 2 # TODO: Make this a parm?
			maxXres = 520
			if res[0] > maxXres:
				y = int(res[1] * float(maxXres)/res[0])
				res = (maxXres, y)
			self.displayRes = res
			self.reloadErrorImg()
			#loadedImg = loadedImg.resize((res[0]*sc, res[1]*sc), Image.ANTIALIAS)
			loadedImg = loadedImg.resize((res[0], res[1]), Image.ANTIALIAS)
			img = ImageTk.PhotoImage(loadedImg)
			print "_safeLoad(): success!"
		else:
			img = self.staticImages["error"]
			print "_safeLoad(): ********** FAIL! **********"
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
				os.remove(destPath)
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



	def __init__(self):
		# Needed for pickling.
		lim = sys.getrecursionlimit()
		sys.setrecursionlimit(lim*1000)

		self.getImgDebugFunctions = {
				"name":[self.getImgDebug1, self.getImgDebug2],
				"lev":[self.getLevDebug1, self.getLevDebug2]
		}
		self.parmDic = ut.parmDic(parmPath)
		print "\n\n\n__init__():********** parmDic2"
		print self.parmDic
		self.pauseSaveUIToParmsAndFile = False
		self.parmEntries = {}
		self.renQLs = []
		self.seqDataDir = ut.dataDir + "/" + self.parmDic("image")
		self.seqDataVDir = self.seqDataDir + "/" + self.parmDic("dataVer")
		self.seqRenDir = ut.renDir + "/" + self.parmDic("image")
		self.seqRenVDir = self.seqRenDir + "/" + self.parmDic("renVer")

		self.timerStarts = {}
		global statsDirDest # for cProfile
		statsDirDest = self.seqRenVDir 
		self.inSurfGridPrev = None
		self.setVal("anim", 0)
		nLevels = self.parmDic("nLevels")
		self.updateRenAndDataDirs()
		self.nextSid = 0
		self.tidToSids = None
		self.sidToTid = None
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

		sourceImages = os.listdir(ut.imgIn)
		sourceImages.sort()


		# TODO e needed?
		self.root.bind('<Return>', lambda e: self.returnCmd())
		#self.root.bind('<KeyPress>', self.keyPress)
		for kk in ["Left", "Right", "Escape", "Control-Left", "Control-Right", "space", "c", "r", "x"]:
			self.root.bind('<' + kk + '>', self.execHotkey)
		self.root.bind('<Control-Left>', lambda e: self.rewButCmd())
		self.root.bind('<Control-Right>', lambda e: self.ffwButCmd())

		#self.root.bind('<Control-Left>', lambda e: self.rewButCmd())
		# Load images.
		self.staticImageNames = ["play", "pause", "rew", "stepBack", "stepFwd", "ffw", "recOn", "recOff", "error"]
		self.varyingStaticImageNames = ["anim", "rec"]
		self.staticImages = {}
		base = ut.imgDir + "/controls/"
		self.errorImgPath = base + "error.jpg"
		for name in self.staticImageNames:
			loadedImg = Image.open(base + name + ".jpg")
			print "__init__(): loadedImg", loadedImg
			#res = loadedImg.size
			#sc = 2
			#loadedImg = loadedImg.resize((res[0]*sc, res[1]*sc), Image.ANTIALIAS)
			self.staticImages[name] = ImageTk.PhotoImage(loadedImg)
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
			print "__init__(): --- self.verUI[verType][\"menuVar\"].get()", self.verUI[verType]["menuVar"].get()
			vers = self.getSeqVersions(verType)
			print "\n__init__(): " + verType + " vers:", vers

			print "\n\n__init__(): YYYYY setting up OptionMenu for", verType
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
		print "__init__(): =========== PATH", path
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
			print "__init__(): \\\\\\\\\\\\ col", col, "dbImgName", dbImgName
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
		print "\n__init__():  ****** doing self.getImg", self.parmDic("image")
		self.getImg(self.parmDic("image")) 
		while not self.rootDestroyed:
			anim = self.parmDic("anim")
			if anim == 1:
				frStart = self.parmDic("frStart")
				frEnd = self.parmDic("frEnd")
				fr = self.parmDic("fr")
				frPerCycle = self.parmDic("frPerCycle")
				nLevels = self.parmDic("nLevels")
				secondsPassed = time.time() - self.timeStart

				newFr = self.frStartAnim + int(secondsPassed*self.parmDic("fps"))
				if newFr > fr:		
					fr = min(fr + 1, newFr)
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

					print "__init__(): statsMsg:", statsMsg
					with open(self.seqRenVDir + "/stats", 'w') as f:
						f.write(statsMsg)


					if fr > self.parmDic("frEnd"):
						if self.record:
							# Global varable needed for final stats
							statsDirDest = self.seqRenVDir 
							# TODO: rename - for now doRenCv=currently doing ren; doRen=you should do ren
							if self.parmDic("doRenCv") == 0 and self.parmDic("doRen") == 1:
								# Restart and do renCv

								# Write stats
								secondsPassed = time.time() - self.timeStart
								hmsPassed = ut.secsToHms(secondsPassed)
								ut.writeTime(self, "totalTimeOfAnim", hmsPassed)

								print "__init__(): Turning on doRenCv"
								self.setVal("doRenCv", 1)
								self.chk_doRenCv_var.set(1)
								print "__init__(): Returning to", self.parmDic("frStart")
								fr = self.parmDic("frStart")
							elif self.parmDic("image") in self.renQLs and not self.parmDic("image") == self.renQLs[-1]:
								# If recording and in renQ but not last,
								# turn off doRenCv, restart, and got to next img.
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
							print "__init__(): Returning to", self.parmDic("frStart")
							fr = self.parmDic("frStart")
							self.timeStart = time.time()
							#self.animFrStart = fr

					# This forces each frame to process, ie. ACTUALLY GENERATES THE DATA.  TODO: maybe add forceFps
					self.setFrAndUpdate(fr)

					# For ofs anim.
					#ofs = fr/float(frPerCycle) % 1
					ofs = self.getOfs() % 1
				self.setVal("fr", fr)
			if not self.rootDestroyed:
				Tk.update_idletasks(self.root)
				Tk.update(self.root)


profiling = False

if profiling:
	cProfile.run('warpUi()', statsObjPathSrc)
	ut.exeCmd("cp " + statsObjPathSrc + " " + statsDirDest)
else:
	warpUi()
	sys.exit()
#with open(path, 'w') as f:
