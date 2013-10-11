#! /usr/bin/python

import random, os
import pygame
from pygame.locals import *
pygame.init()

class World:
	fill_factor = 0.4

	def __init__(self, w, h, seed):
		self.w, self.h, self.seed = w, h, seed
		self.full_row = sum(1<<(5*i) for i in xrange(self.w))
		self.side_row = 1 | (1<<(5*(self.w-1)))

	def seed_dirt(self):
		random.seed(self.seed)
		# Convention: (self.rows[y]>>(x*5))&1
#		self.rows = [self.full_row]
#		for i in xrange(self.h-2):
#			v = 1 | (1<<(5*(self.w-1)))
#			for i in xrange(self.w-2):
#				v |= (1<<(5*(i+1))) * (random.random() < World.fill_factor)
#			assert v ^ (v & self.full_row) == 0
#			self.rows.append(v)
#		self.rows.append(self.full_row)
		self.rows = [self.side_row]*self.h
		for x in xrange(self.w):
			for y in xrange(self.h):
				if random.random() < World.fill_factor:
					self.set_at(x, y, 1)
		self.rows[0] |= self.full_row
		self.rows[-1] |= self.full_row

	def normalize(self, v):
#		v |= v >> 1
#		v |= v >> 2
#		v |= v >> 1
		return (v & self.full_row) | self.side_row

	def sculpt_dirt(self, sculpt_size, first_passes, second_passes):
		self.sculpt_size, self.first_passes, self.second_passes = sculpt_size, first_passes, second_passes
		def mix3(x):
			return x + (x>>5) + (x<<5)
		def mix5(x):
			return x + (x>>5) + (x<<5) + (x>>10) + (x<<10)
		for i in xrange(first_passes+second_passes):
			print "FIRST"
			new = [self.full_row]
			for y in xrange(1, self.h-1):
				v = mix3(self.rows[y-1]) + mix3(self.rows[y]) + mix3(self.rows[y+1])
				v = (v>>3) | ((v>>2) & ((v>>1)|v))
				v = self.normalize(v)
				new.append(v)
			new.append(self.full_row)
			self.rows = new

			if i < first_passes:
				print "SECOND"
				new = [self.full_row, self.rows[1]]
				for y in xrange(2, self.h-2):
					v = mix5(self.rows[y-2]) + mix5(self.rows[y-1]) + mix5(self.rows[y]) + mix5(self.rows[y+1]) + mix5(self.rows[y+2])
					invert = ~v
					v = self.rows[y] | (((invert>>2) & (invert>>3) & (invert>>4)) & (invert | (invert>>1)))
					v = self.normalize(v)
					new.append(v)
				new.append(self.rows[-2])
				new.append(self.full_row)
				self.rows = new

	def get_at(self, x, y):
		return (self.rows[y]>>(x*5))&1

	def set_at(self, x, y, v):
		self.rows[y] |= 1<<(x*5)

	def render(self):
		surf = pygame.Surface((self.w, self.h))
		for y in xrange(self.h):
			for x in xrange(self.w):
				color = [(41,27,2), (108,67,21)][self.get_at(x, y)]
				surf.set_at((x, y), color)
		path = "ff%is%isize%ix%isculpt%i-%i-%i.bmp" % \
			(int((1-World.fill_factor)*100), self.seed, self.w, self.h, self.sculpt_size, self.first_passes, self.second_passes)
		path = os.path.join("output", path)
		pygame.image.save(surf, path)

"ff50s389746size128x40sculpt1-4-3"

w = World(64, 40, 623245)
w.seed_dirt()
w.sculpt_dirt(1, 4, 2)
w.render()

