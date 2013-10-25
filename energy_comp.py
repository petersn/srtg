#! /usr/bin/python

import math
from matplotlib import pyplot as plt
import catenary_solver

p0, p1 = [(5 + i*2*(10/7.0)**0.5)**0.5/3 for i in (-1, 1)]
w0, w1 = [(322 + i*13*70**0.5)/900 for i in (-1, 1)]
quad_points  = [-p1, -p0, 0, p0, p1]
quad_weights = [w0, w1, 128/225.0, w1, w0]

def rf(path):
	data = open(path).readlines()
	data = [line.strip() for line in data]
	data = [line for line in data if line]
	return map(float, data)

quad_points = rf("data/quad_a")
quad_weights = rf("data/quad_w")

def quad(f, a, b):
	"""quad(f, a, b) -> \int_a^b f(x) dx

	Uses some quadrature rule to evaluate the integral.
	"""
	S, D = (b+a)/2.0, (b-a)/2.0
	def rescaled_f(x):
		return f(x*D + S)*D
	return sum(w * rescaled_f(p) for w, p in zip(quad_weights, quad_points))

def catenary_energy(x0, y0, x1, y1, length):
	epsilon = 1e-5
	c1 = catenary_solver.Catenary.from_ABl(x0, y0, x1, y1, length)
	c2 = catenary_solver.Catenary.from_ABl(x0, y0, x1, y1, length+epsilon)
	c3 = catenary_solver.Catenary.from_ABl(x0, y0, x1, y1, length+epsilon*2)
	def norm(p):
		x1 = c1.get_x_by_s(0, p)
		x2 = c2.get_x_by_s(0, p)
		x3 = c3.get_x_by_s(0, p)
		y1 = c1(x1)
		y2 = c2(x2)
		y3 = c3(x3)
		delta1 = x2-x1, y2-y1
		norm1 = (delta1[0]**2 + delta1[1]**2)
		delta2 = x3-x2, y3-y2
		norm2 = (delta2[0]**2 + delta2[1]**2)
		return norm2-norm1
	v = quad(norm, 0, length-epsilon)
#	integral = 0.0
#	samps = 127#20000
#	for p in xrange(samps):
#		p = (p/(samps-1.0)) * (length-epsilon)
#		n = norm(p)
#		integral += n/float(samps) * (length-epsilon)
#	print "Obvious rule:", integral / epsilon
#	print "Gauss:", v / epsilon
	return v / epsilon

# dE/dt = f . v

catenary_energy(0, 0, 1, 3, 5)

