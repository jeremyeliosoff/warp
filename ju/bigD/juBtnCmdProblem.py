#!/usr/bin/python
from Tkinter import *

root = Tk()
frame = Frame(root)
frame.pack()

def pr(s):
	print s

for num in ["one", "two", "three"]:
	Button(frame, text=num, command=lambda t=num: pr(t)).pack()

mainloop()
