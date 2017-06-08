#!/usr/bin/python
import sys, os, random, re, glob, pprint

# GLOBAL VARIABLES
projDir = "/home/jeremy/dev/warp"
dataDir = projDir + "/data"
renDir = projDir + "/ren"
framesDir = dataDir + "/frames"

seqDir = projDir + "/seq"

imgDir = projDir + "/img"
imgIn = imgDir + "/input"

# TODO Why is there anim and play
staticImgPaths = {
    "play":imgDir + "/controls/play.jpg",
    "pause":imgDir + "/controls/pause.jpg",
    "rew":imgDir + "/controls/rew.jpg",
    "ffw":imgDir + "/controls/ffw.jpg",
}

# CLASSES
class parmDic:
    parmFile = None
    parmDic = {}
    parmStages = {}
    parmLs = []

    def loadParmLs(self, parmFile=None):
        if parmFile == None:
            parmFile = self.parmFile
        #print "\n\n\n"
        #print "\n\n\n INSIDE loadParmLs"
        self.parmLs = []
        thisParmDic = {}
        thisParmName = ""
        thisStage = "META"
        nextIsParm = True # nextIsParmOrDivider, really
        with open(parmFile) as f:
            for line in f.readlines():
                stripped = line.strip()
                if stripped == "":
                    nextIsParm = True
                else:
                    if nextIsParm:
                        if stripped[:3] == "---" and stripped[-3:] == "---":
                            thisStage = stripped[3:-3]
                            continue

                        if not thisParmName == "":
                            # This isn't the beginnig of file/stage; store previously collecte attrs.
                            self.parmLs.append([thisParmName, thisParmDic])
                        thisParmName = stripped
                        thisParmDic = {"stage":thisStage}
                    else:
                        k,v = stripped.split()
                        thisParmDic[k] = v
                        
                    nextIsParm = False
                #print "-----------"
                #print "line:", line
                #print "stripped:", stripped
                #print "nextIsParm:", nextIsParm

        self.parmLs.append([thisParmName, thisParmDic])
        print "\n\n\nparmLs"
        print self.parmLs

    def parmLsToDic(self):
        self.parmDic = {}
        for k,v in self.parmLs:
            print "loading parm " + k + ", dic:", v
            self.parmDic[k] = v
            if "stage" in v.keys(): # Should always be true
                stage = v["stage"]
                if stage in self.parmStages.keys():
                    self.parmStages[stage].append(k)
                else:
                    self.parmStages[stage] = [k]


    def loadParms(self, parmFile=None):
        self.loadParmLs(parmFile)
        self.parmLsToDic()

    def __call__(self, parmStr):
        thisParmDic = self.parmDic[parmStr]
        strVal = thisParmDic["val"]
        typ = thisParmDic["type"]
        if typ == "int":
            return int(strVal)
        elif typ == "float":
            return float(strVal)
        elif typ == "clr":
            return tuple([float(i) for i in strVal.split(",")])
        else:
            return strVal

    def __init__(self, parmFile):
        self.parmFile = parmFile
        self.loadParms()
    

# FUNCTIONS

# os
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


def isScalar(v):
    return isinstance(v, float) or isinstance(v, int)

def clamp(v, mn, mx):
    if isScalar(v):
        return max(min(v, mx), mn)
    else:
        vmn = (mn, mn, mn) if isScalar(mn) else mn
        vmx = (mx, mx, mx) if isScalar(mx) else mx
        return vMax(vMin(v, vmx), vmn)


def vDiff(a, b):
    ret = []
    for i in range(len(a)):
        ret.append(b[i] - a[i])
    return ret


def vAdd(a, b):
    ret = []
    for i in range(len(a)):
        ret.append(a[i] + b[i])
    return ret

def vMin(a, b):
    ret = []
    for i in range(len(a)):
        if isScalar(b):
            ret.append(min(a[i], b))
        else:
            ret.append(min(a[i], b[i]))
    return ret

def vMax(a, b):
    ret = []
    for i in range(len(a)):
        if isScalar(b):
            ret.append(max(a[i], b))
        else:
            ret.append(max(a[i], b[i]))
    return ret

def vMult(a, b):
    ret = []
    for i in range(len(a)):
        if isScalar(b):
            ret.append(a[i] * b)
        else:
            ret.append(a[i] * b[i])
    return ret

def gamma(a, g):
    return pow(a, 1.0/g)

def vGamma(a, g):
    ret = []
    for i in range(len(a)):
        if isScalar(g):
            ret.append(gamma(a[i], g))
        else:
            ret.append(gamma(a[i], g[i]))
    return ret

def vNeg(a):
    return vMult(a, -1)

def exeCmd(cmd):
    print "executing", cmd
    os.system(cmd)

def mix(a, b, m):
    if isScalar(a):
        return a*(1-m) + b*m
    else:
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

def ranClr(seed):
	random.seed(seed)
	return [random.random(), random.random(), random.random()] 


# NAVAGATION


#def getVersions(verType, seq=None):
def getVersions(verDir):
    #if seq == None:
    #    verDir = self.seqDataDir if verType == "data" else self.seqRenDir
    #elif verType == "data":
    #    verDir = dataDir + "/" + seq
    #else:
    #    verDir = renDir + "/" + seq

    vers = [f for f in os.listdir(verDir) if re.match('v[0-9][0-9][0-9]*', f)]
    vers.sort()
    vers.reverse()

    # Make v000 dir if there is none.
    if vers == []:
        mkDirSafe(verDir + "/v000")
        vers = ["v000"]

    return vers

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
    seqs = glob.glob(verDir + pref + "*")
    seqs.sort(key=os.path.getmtime)
    #print "seqs"
    #pprint.pprint(seqs)
    seqPath = seqs[-1]
    #seq = seqPath.split("/")[-1]
    #print "hhhhhhhey - seq:", seq
    vers = getVersions(seqPath)
    vers.sort()
    #print "verDir"
    #print verDir
    #print "seqPath"
    #print seqPath
    #print "vers"
    #pprint.pprint(vers)
    verPath = seqPath + "/" + vers[-1]
    if verType == "ren":
        verPath += "/ren/ALL"
    print verPath
    return "fuck"

if __name__ == "__main__":
    main()
