#!/usr/bin/python
import pygame, sys

for src in sys.argv[1:]:
	print "Processing " + src + "..."

	img = pygame.image.load(src)
	sx,sy = img.get_size()

	nsy = int(sy * 1.08)
	nsx = int(nsy * 1.5)
	padx = int((nsx - sx)/2)
	pady = int((nsy - sy)/2)
	newImg = pygame.Surface((nsx, nsy))

	for x in range(nsx):
		for y in range(nsy):
			newImg.set_at((x, y), (100, 100, 100))
	for x in range(sx):
		for y in range(sy):
			clr = img.get_at((x, y))
			newImg.set_at((padx+x,pady+y), clr)

	words = src.split('.')
	words.insert(-1, "pad")
	newName = ".".join(words)
	pygame.image.save(newImg, newName)
	print "\tsaving " + newName + "..."
