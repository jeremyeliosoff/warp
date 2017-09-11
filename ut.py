#!/usr/bin/python
import sys, os, random, re, glob, pprint, inspect, math, time, psutil

# GLOBAL VARIABLES
projDir = "/home/jeremy/dev/warp"
dataDir = projDir + "/data"
renDir = projDir + "/ren"
framesDir = dataDir + "/frames"
parmsPath = projDir + "/parms"
parmsDefPath = projDir + "/parmsDef"
statImgExt = ".jpg"

seqDir = projDir + "/seq"

imgDir = projDir + "/img"
imgIn = imgDir + "/input"

# TODO Why is there anim and play
staticImgPaths = {
	"play":imgDir + "/controls/play" + statImgExt,
	"pause":imgDir + "/controls/pause" + statImgExt,
	"rew":imgDir + "/controls/rew" + statImgExt,
	"ffw":imgDir + "/controls/ffw" + statImgExt,
}

# CLASSES
class parmDic:
	parmPath = None
	parmDic = {}
	parmStages = {}
	parmLs = []

	def loadParmLs(self, parmPath=None):
		print "\n\n_loadParmLs(): BEGIN: parmPath:", parmPath
		#self.parmLs = []
		thisParmDic = {}
		alreadyInList = False
		thisParmName = ""
		thisStage = "META"
		nextIsParmOrDivider = True
		parmFileTail = parmPath[-10:]
		with open(parmPath) as f:
			for line in f.readlines():
				stripped = line.strip()
				print "_loadParmLs(): parmPath:" + parmFileTail + \
					", stage:" + thisStage + ", line:", stripped
				if stripped == "":
					nextIsParmOrDivider = True
				else:
					if nextIsParmOrDivider:
						if stripped[:3] == "---" and stripped[-3:] == "---":
							thisStage = stripped[3:-3]
							continue

						if not thisParmName == "":
							# TODO: Why would the parm already be in list?
							alreadyInList = False
							#print "_loadParmLs(): adding dic for parm:", thisParmName+":"
							#print "_loadParmLs():\t", thisParmDic
							for i,nameAndDic in enumerate(self.parmLs):
								if nameAndDic[0] == thisParmName:
									self.parmLs[i][1] = thisParmDic
									alreadyInList = True
									#print "_loadParmLs():\t", thisParmName, \
									#	"alreadyInList! Setting to", thisParmDic

							if not alreadyInList:
								self.parmLs.append([thisParmName, thisParmDic])

						thisParmName = stripped
						#print "_loadParmLs():\t\tthisParmName:", thisParmName
						if thisParmName in self.parmDic.keys():
							# Add "stage" attr to this parm if it exists in dic...
							thisParmDic = self.parmDic[thisParmName]
							# Stage is determined by first (default) list.
							if not alreadyInList:
								thisParmDic["stage"] = thisStage
						else:
							#...else init dictionary with just stage attr
							thisParmDic = {"stage":thisStage}
					else:
						k,v = stripped.split()
						# Force animation off when loaded (should normally already be so)
						if thisParmName == "anim" and k == "val":
							v = "0"

						# Force type changes, kinda backward compatibility
						if thisParmName == "doRenCv" and k == "type":
							v = "bool"
						thisParmDic[k] = v
						
					nextIsParmOrDivider = False

		# Needed for last parm, I think.
		if not alreadyInList:
			self.parmLs.append([thisParmName, thisParmDic])

		print "\n\n_loadParmLs(): self.parmLs:"

		for pm in self.parmLs:
			print "\n\n_loadParmLs():\t", pm
		print "\n\n_loadParmLs(): END"



	def parmLsToDic(self):
		#self.parmDic = {}
		#print "\n\n_parmLsToDic BEGIN"

		#TODO Maybe make this a list
		self.parmStages = {}
		for k,v in self.parmLs:
			self.parmDic[k] = v
			if "stage" in v.keys(): # Should always be true
				stage = v["stage"]
				if stage in self.parmStages.keys():
					self.parmStages[stage].append(k)
				else:
					self.parmStages[stage] = [k]


	def loadParms(self, parmPath):
		self.loadParmLs(parmPath)
		self.parmLsToDic()

	# This should maybe be in a separate utility script?
	def __call__(self, parmStr):
		thisParmDic = self.parmDic[parmStr]
		strVal = thisParmDic["val"]
		typ = thisParmDic["type"]
		if typ in ["int", "bool"]:
			return int(strVal)
		elif typ == "float":
			return float(strVal)
		elif typ == "clr":
			return tuple([float(i) for i in strVal.split(",")])
		else:
			return strVal

	def __init__(self, parmPath):
		self.loadParms(parmsDefPath)
		self.loadParms(parmsPath)
	

# FUNCTIONS

# os

def safeRemove(path):
	print "_safeRemove(): path =", path
	if os.path.exists(path):
		print "_safeRemove(): exists, removing..."
		os.remove(path)

def safeMakeEmptyFile(path):
	print "_safeMakeEmptyFile(): path =", path
	if not os.path.exists(path):
		print "_safeMakeEmptyFile(): doesn't exist, making..."
		os.mknod(path)


def exeCmd(cmd):
	print "executing", cmd
	os.system(cmd)

def mkDirSafe(path):
	if not os.path.isdir(path):
		#print "Making dir:", path
		os.makedirs(path)

# Colours, rgb + tex
def rgbInt_to_hex(c):
	"""Return color as #rrggbb for the given color values."""
	return '#%02x%02x%02x' % tuple(c)
def rgb_dec_to_int(c):
	return [int(r*255) for r in c]

def rgb_int_to_dec(c):
	return [float(r)/255 for r in c]

def rgb_to_hex(c):
	cc = rgb_dec_to_int(c)
	return rgbInt_to_hex(cc)


# Vector + scalar operations
def isScalar(v):
	return isinstance(v, float) or isinstance(v, int)

def clamp(v, mn, mx):
	return max(min(v, mx), mn)

def clampV(v, mn, mx):
	return maxV(minV(v, vmx), vmn)

def clampVSc(v, mn, mx):
	vmn = tuple([mn]*len(v))
	vmx = tuple([mx]*len(v))
	return maxV(minV(v, vmx), vmn)


def vDiff(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(b[i] - a[i])
	return ret

def vAvg(a):
	tot = 0
	for v in a:
		tot += v
	return float(tot)/len(a)

def vLen(a):
	tot = 0
	for v in a:
		tot += v*v
	return math.sqrt(tot)

def vDist(a, b):
	aToB = vDiff(b, a)
	return vLen(aToB)


def vAdd(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(a[i] + b[i])
	return ret

def minVSc(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(min(a[i], b))
	return ret

def minV(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(min(a[i], b[i]))
	return ret

def maxVSc(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(max(a[i], b))
	return ret

def maxV(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(max(a[i], b[i]))
	return ret

def multVSc(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(a[i] * b)
	return ret

def multV(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(a[i] * b[i])
	return ret

def gamma(a, g):
	return pow(a, 1.0/g)

def gammaV(a, g):
	ret = []
	for i in range(len(a)):
		ret.append(gamma(a[i], g[i]))
	return ret

def gammaVSc(a, g):
	ret = []
	for i in range(len(a)):
		ret.append(gamma(a[i], g))
	return ret

def vNeg(a):
	return multVSc(a, -1)

def exeCmd(cmd):
	print "executing", cmd
	os.system(cmd)

def mix(a, b, m):
	return a*(1-m) + b*m

def mixV(a, b, m):
	ret = []
	for i in range(len(a)):
		ret.append(a[i]*(1-m) + b[i]*m)
	return ret

def vAdd(a, b):
	ret = []
	for i in range(len(a)):
		ret.append(a[i] + b[i])
	return ret

def smoothstep(edge0, edge1, x):
	# Scale, bias and saturate x to 0..1 range
	ret = edge1
	if edge1 > edge0:
		x = clamp((x - edge0)/(edge1 - edge0), 0.0, 1.0); 
		# Evaluate polynomial
		ret = x*x*(3 - 2*x);
	return ret

def smoothpulse(in0, in1, out0, out1, x):
	return smoothstep(in0, in1, x) - smoothstep(out0, out1, x)

def ranClr(seed):
	random.seed(seed)
	return [random.random(), random.random(), random.random()] 


# NAVAGATION


#def getVersions(verType, seq=None):
def getVersions(verDir):
	#if seq == None:
	#	verDir = self.seqDataDir if verType == "data" else self.seqRenDir
	#elif verType == "data":
	#	verDir = dataDir + "/" + seq
	#else:
	#	verDir = renDir + "/" + seq

	vers = [f for f in os.listdir(verDir) if re.match('v[0-9][0-9][0-9]*', f)]
	vers.sort()
	vers.reverse()

	# Make v000 dir if there is none.
	if vers == []:
		mkDirSafe(verDir + "/v000")
		vers = ["v000"]

	return vers

def secsToHms(s):
	m, s = divmod(s, 60)
	h, m = divmod(m, 60)
	return "%d:%02d:%02d" % (h, m, s)

def hmsToSecs(hms):
	h, m, s = hms.split(":")
	return float(s) + float(m)*60 + float(h)*60*60

def printFrameStack():
	curframe = inspect.currentframe()
	calframe = inspect.getouterframes(curframe, 2)
	print "\n*FRAME STACK* in",
	first = True
	for i in calframe[1:]:
		if first:
			print " [ " + str(i[3]) + " ], called by:",
		else:
			print " " + str(i[3]),
		first = False
	print


def writeTime(warpUi, label, time):
	if warpUi.writeTimerStats:
		if warpUi.parmDic("doRenCv") == 1:
			destDir = warpUi.seqRenVDir 
		else:
			destDir = warpUi.seqDataVDir

		toWrite = label + " " + str(time)
		destPath = destDir + "/statsPrintout"
		with open(destPath, 'a') as f:
			f.write(toWrite + "\n")

def timerStart(warpUi, label):
	if warpUi.writeTimerStats:
		warpUi.timerStarts[label] = time.time()

def timerStop(warpUi, label):
	if warpUi.writeTimerStats:
		writeTime(warpUi, label, time.time() - warpUi.timerStarts[label])

def recordMemUsage(path):
	process = psutil.Process(os.getpid())
	return process.memory_percent()
	


def main():
	verType = sys.argv[1]
	pref = ""
	if len(sys.argv) > 2:
		pref = sys.argv[2]
	if verType == "data":
		verDir = dataDir + "/"
		#seqs = glob.glob(dataDir + "/" + pref + "*")
	else:
		verDir = renDir + "/"
	dirs = glob.glob(verDir + pref + "*")
	dirs.sort(key=os.path.getmtime)
	dirPath = dirs[-1]
	vers = getVersions(dirPath)
	vers.sort()
	verPath = dirPath + "/" + vers[-1]
	if verType == "renImg":
		verPath += "/ren/ALL"
	print verPath # Don't pad this with "ut.py():", it's used by clr, cld, etc.
	return "fuck"

if __name__ == "__main__":
	main()
