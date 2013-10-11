#! /usr/bin/python

import srt_solver
from pygame.locals import *
import pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

rope = srt_solver.Rope(None, 300)
rope.constrain(srt_solver.PointConstraint(0, (50, -50)))
rope.constrain(srt_solver.PointConstraint(70.75, (100, -100)))
rope.constrain(srt_solver.PointConstraint(300, (150, -150)))
rope.rebuild_models()

mouse_holding = False

while True:
	mouse_x, mouse_y = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == 27):
			pygame.quit()
			raise SystemExit
		if event.type == MOUSEBUTTONDOWN:
			if event.button == 1:
				mouse_holding = True
		if event.type == MOUSEBUTTONUP:
			if event.button == 1:
				mouse_holding = False

	screen.fill((255,255,255))

	points = []
	for s in xrange(0, 301):
		x, y = rope.get_xy(s)
		points.append((x, -y))
	pygame.draw.lines(screen, (0,0,0), False, points, 3)

	pygame.display.update()
	clock.tick(60)

