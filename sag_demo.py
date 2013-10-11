#! /usr/bin/python

import parabola_solver
import catenary_solver
import srt_fe
from pygame.locals import *
import pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

rope = srt_fe.Rope(None, 300, 20, 400)

arc_x, arc_y = 300, 20

mouse_holding = None

params = cat = None

while True:
	mouse_x, mouse_y = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == 27):
			pygame.quit()
			raise SystemExit
		if event.type == MOUSEBUTTONDOWN:
			if event.button == 1:
				mouse_holding = min(rope.segs, key=lambda seg: (seg.x-mouse_x)**2 + (seg.y-mouse_y)**2)
		if event.type == MOUSEBUTTONUP:
			if event.button == 1:
				mouse_holding = None
		if event.type == KEYDOWN:
			if event.key == K_UP:
				mouse_holding = mouse_holding.next
			if event.key == K_DOWN:
				mouse_holding = mouse_holding.prev

	screen.fill((255,255,255))

	for length in (400,):#(200, 300, 400, 500):
		try:
			params = parabola_solver.fit_parabola(arc_x, -arc_y, mouse_x, -mouse_y, length)
		except AssertionError:
			params = None
		try:
			cat = catenary_solver.Catenary.from_ABl(arc_x, -arc_y, mouse_x, -mouse_y, length)
		except AssertionError:
			cat = None

		xs = range(min(arc_x, mouse_x), max(arc_x, mouse_x)+1)
		do = []
		if params:
			p_ys = [-parabola_solver.parabola(x, params) for x in xs]
			do.append(((255,0,0), p_ys))
		if cat:
			c_ys = [-cat(x) for x in xs]
			do.append(((0,255,0), c_ys))
		for color, ys in do:
			points = zip(xs, ys)
			if len(points) > 1:
				try:
					pygame.draw.lines(screen, color, False, points, 3)
				except:
					print points

	points = [(seg.x, seg.y) for seg in rope.segs]
	pygame.draw.lines(screen, (0,0,0), False, points)
	for p in points:
		pygame.draw.circle(screen, (0,0,0), map(int, p), 3)

	for i in xrange(100):
		rope.update(0.01)
		rope.segs[0].x, rope.segs[0].y = 300, 20
		rope.segs[0].xv, rope.segs[0].yv = 0, 0
		if mouse_holding:
			mouse_holding.x = mouse_x
			mouse_holding.y = mouse_y
			mouse_holding.xv = 0
			mouse_holding.yv = 0
#		rope.segs[-1].x, rope.segs[-1].y = 450, 150

	pygame.display.update()
	clock.tick(60)

