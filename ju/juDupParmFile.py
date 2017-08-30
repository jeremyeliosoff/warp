#!/usr/bin/python
import pygame, os, sys, glob
from shutil import copyfile
#"angel_50pct_vig":"1-300",
rangeDic ={ "balance_50pct_vig":"1-101",
"canopy_50pct_vig":"100-400",
"cityMs03_50pct_vig":"100-500",
"dance_50pct_vig":"280-430",
"fbLs04_50pct_vig":"200-400",
"frolick02_50pct_vig":"350-550",
#"hotdog_50pct_vig":"75-375",
"angel_50pct_vig":"1-300",
"mowJog_50pct_vig":"1850-2059",
"mtnFromConc3_50pct_vig":"10-210",
"sunbeam_50pct_vig":"43-243",
"tamFlip_50pct_vig":"570-670",
"tamInCrowdSm_50pct_vig":"200-400",
"vol_50pct_vig":"850-1050"}
#template = "angel_50pct_vig"
template = "hotdog_50pct_vig"
for dest,rng in rangeDic.items():
	copyfile(template, dest)
	os.system("sed -i -- s/range.*/range="+ rng +"/g " + dest)
	os.system("sed -i -- s/"+ template + "/" + dest + "/g " + dest)
