#!/usr/bin/python
import os

# GLOBAL VARIABLES
projDir = "/home/jeremy/dev/warp"
dataDir = projDir + "/data"
framesDir = dataDir + "/frames"

seqDir = projDir + "/seq"

imgDir = projDir + "/img"
imgIn = imgDir + "/input"
imgPlay = imgDir + "/controls/play.jpg"
imgPause = imgDir + "/controls/pause.jpg"

imagePaths = {
    "source":imgDir + "/ui/glow.jpg",
    "out":imgDir + "/ui/out.jpg",
    "play":imgDir + "/controls/play.jpg",
    "pause":imgDir + "/controls/pause.jpg",
    "anim":imgDir + "/controls/pause.jpg",
}

# CLASSES
class parmDic:
    parmFile = None
    parmDic = {}
    parmLs = []

    def loadParmLs(self):
        #print "\n\n\n"
        #print "\n\n\n INSIDE loadParmLs"
        self.parmLs = []
        thisParmDic = {}
        thisParmName = ""
        nextIsParm = True
        with open(self.parmFile) as f:
            for line in f.readlines():
                stripped = line.strip()
                if stripped == "":
                    nextIsParm = True
                else:
                    if nextIsParm:
                        if not thisParmName == "":
                            self.parmLs.append([thisParmName, thisParmDic])
                        thisParmName = stripped
                        thisParmDic = {}
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


    def loadParms(self):
        self.loadParmLs()
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
def mkDirSafe(path):
    if not os.path.isdir(path):
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
