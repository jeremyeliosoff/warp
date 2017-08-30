#!/usr/bin/python
import pickle, sys, os, glob
picFile=sys.argv[1]

f = open(picFile, 'r')
struc = pickle.load(f)
f.close()

def printRecur(s, indent):
	if isinstance(s, float) or isinstance(s, int) or isinstance(s, str):
		print indent, s
	elif isinstance(s, list) or isinstance(s, tuple) or isinstance(s, set):
		print indent, "printing list:"
		for ss in s:
			printRecur(ss, indent + " ")
	elif isinstance(s, dict):
		print "\n", indent, "printing dic:"
		#for k,v in s.items():
		ks = s.keys()
		ks.sort()
		ks.reverse()
		for k in ks:
			v = s[k]
			print indent, "key", k, "value:"
			printRecur(v, indent + " ")

printRecur(struc, "")
