#!/usr/bin/python
import os

# GLOBAL VARIABLES
projDir = "/home/jeremy/dev/warp"
dataDir = projDir + "/data"
framesDir = dataDir + "/frames"

imgDir = projDir + "/img"
imgPath = imgDir + "/single/testAndP.jpg"
#imgPath = imgDir + "/img/single/glow.jpg"
imgPathOut = imgDir + "/single/levelImg.jpg"
imgPathCurves = imgDir + "/single/curves.jpg"
imgTmp = imgDir + "/tmp"
imgTest = imgDir + "/test"
imgJtGrid = imgTmp + "/jtGrid.jpg"
imgPlay = imgDir + "/controls/play.jpg"
imgPause = imgDir + "/controls/pause.jpg"

imagePaths = {
    "orig":imgDir + "/single/glow.jpg",
    "levels":imgDir + "/single/levelImg.jpg",
    "curves":imgDir + "/single/curves.jpg",
    "jtGrid":imgTmp + "/jtGrid.jpg",
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
                print "line:", line
                #print "stripped:", stripped
                #print "nextIsParm:", nextIsParm

        self.parmLs.append([thisParmName, thisParmDic])
        print "\n\n\nparmLs"
        print self.parmLs

    def parmLsToDic(self):
        self.parmDic = {}
        for k,v in self.parmLs:
            print "k", k
            print "v", v
            print
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
        else:
            return strVal

    def __init__(self, parmFile):
        self.parmFile = parmFile
        self.loadParms()
    

# FUNCTIONS
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

def getParmVal(parmDic, parm):
    thisParmDic = parmDic.parmDic[parm]
    strVal = thisParmDic["val"]
    typ = thisParmDic["type"]
    if typ == "int":
        return int(strVal)
    elif typ == "float":
        return float(strVal)
    else:
        return strVal
