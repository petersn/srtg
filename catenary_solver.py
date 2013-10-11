#! /usr/bin/python
"""
Catenary solver.
"""

# Mathematica was used to derive much of this code!
#   catenary = ym + a Cosh[(x - xm)/a]

import math
import functools
import srt_solver

class BadFittingException(Exception):
	pass

def solve_system(matrix, y):
	"""solve_system(matrix, y) -> x

	Yields x such that matrix * x == y.
	The matrix is given in the form [row1, row2].
	Explicitly, matrix[i][0] * x[0] + matrix[i][1] * x[1] == y[i].
	"""
	(a, b), (c, d) = matrix[0], matrix[1]
	det = float(a * d - b * c)
	if det == 0:
		raise BadFittingException("singular Jacobian")
	a, b, c, d = [i/det for i in (d, -b, -c, a)]
	return a * y[0] + b * y[1], c * y[0] + d * y[1]

def takes_floats(f):
	@functools.wraps(f)
	def wrapper(*args, **kwargs):
		args = map(float, args)
		return f(*args, **kwargs)
	return wrapper

class Catenary:
	def __init__(self, xm, ym, a):
		self.xm, self.ym, self.a = xm, ym, a
		if a <= 0:
			raise BadFittingException("a <= 0")

	def __call__(self, x):
		return self.ym + self.a * math.cosh((x - self.xm) / self.a)

	def get_x_by_s(self, x0, s):
		"""get_x_by_s(self, x0, s) -> x

		Gives x such that self.arc_length(x0, x) == s.
		"""
		s += self.arc_length_indef(x0)
		x = self.xm + self.a * math.asinh(s / self.a)
		return x

	def tension(self, x):
		"""tension(self, x) -> d (units of meters)

		Gives a result d such that d*l*g is the tension, for linear density l and gravitational acceleration g.
		"""
		slope = self.deriv(x)
		return self.a * (slope**2+1)**0.5

	def tangent(self, x):
		dx, dy = 1, self.deriv(x)
		norm = (dx**2 + dy**2)**0.5
		return dx/norm, dy/norm

	def deriv(self, x):
		return math.sinh((x - self.xm) / self.a)

	def second_deriv(self, x):
		return math.cosh((x - self.xm) / self.a) / self.a

	def arc_length_indef(self, x):
		return self.a * math.sinh((x - self.xm) / self.a)

	def arc_length(self, low, high):
		return self.arc_length_indef(high) - self.arc_length_indef(low)

	@staticmethod
	def from_x0y0ddd(x0, y0, d, dd):
		"""from_x0y0ddd(x0, y0, d, dd) -> Catenary

		The returned catenary passes through the given point with derivative d, and second derivative dd.
		"""
		# FullSimplify[Solve[catenary == y0 && D[catenary, x] == d && D[catenary, {x, 2}] == dd, {xm, ym, a}, Reals]]
		a = (1 + d**2)**0.5 / dd
		xm = x0 - (1 + d**2)**0.5 * math.asinh(d) / dd
		ym = y0 - (1 + d**2.0) / dd
		return Catenary(xm, ym, a)

	@staticmethod
	def arclen_grad_x0y0ddd(x0, y0, d, dd, low, high):
		"""arclen_grad_x0y0ddd(x0, y0, d, dd, low, high) -> (alpha, beta, gamma)

		Where arc = Catenary.from_x0y0ddd(x0, y0, d, dd).arc_length(low, high),
			(D[arc, x0], D[arc, d], D[arc, dd])
		"""
		# gA = Sqrt[1 + d^2] / dd;
		# gxm = x0 - Sqrt[1 + d^2] ArcSinh[d]/dd;
		# gym = y0 - (1 + d^2)/dd;
		# arc = gA Sinh[(high - gxm)/gA] - gA Sinh[(low - gxm)/gA];

		f1 = lambda func, bound: func(dd * (bound - x0)/(1 + d**2)**0.5 + math.asinh(d))
		term = f1(math.sinh, high) - f1(math.sinh, low)
		term *= (1 + d**2)**0.5

		# D[arc, x0]
		alpha = f1(math.cosh, low) - f1(math.cosh, high)

		# D[arc, d]
		beta = (1 + d**2 + d * dd * (x0 - high)) * f1(math.cosh, high)
		beta -= (1 + d * (d - dd * low + dd * x0)) * f1(math.cosh, low)
		beta += d * term
		beta /= (1 + d**2.0) * dd

		# D[arc, dd]
		gamma = dd * (high - x0) * f1(math.cosh, high)
		gamma += dd * (x0 - low) * f1(math.cosh, low)
		gamma -= term
		gamma /= dd**2.0

		return alpha, beta, gamma

	newton_schedules = [
		[
			(0.1, 5),
			(1, 10),
		],
		[
			(0.01, 20),
			(0.02, 20),
			(0.04, 20),
			(0.08, 20),
			(0.16, 20),
			(1, 10),
		],
		[
			(0.002, 100),
			(0.004, 100),
			(0.008, 100),
			(0.016, 100),
			(0.032, 100),
			(0.064, 100),
			(0.128, 100),
			(1, 10),
		],
	]

	@staticmethod
	def from_ABl(x0, y0, x1, y1, length):
		# wlog, let x0 < x1.
		flip = x0 > x1
		if flip:
			x0, y0, x1, y1 = x1, y1, x0, y0
		for schedule in Catenary.newton_schedules:
			try:
				cat = Catenary.scheduled_from_ABl(x0, y0, x1, y1, length, newton_schedule=schedule)
			except BadFittingException:
				continue
			if abs(cat(x0)-y0) < 1e-9 and abs(cat(x1)-y1) < 1e-9 and abs(cat.arc_length(x0, x1)-length) < 1e-9:
				return cat
		raise Exception("we had no schedule slow enough to work!")

	@staticmethod
	def scheduled_from_ABl(x0, y0, x1, y1, length, newton_schedule):
		"""from_ABl(x0, y0, x1, y1, length) -> Catenary

		The returned catenary passes through the given points, and has the given arc length.
		"""
		assert x0 != x1
		point_sep = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
		assert point_sep < length
		# To start with, for dd chosen by the below heuristic, compute d to hit the target assuming a parabolic fit.
		dd = (length / abs(x0-x1))**2
		error = y1 - (y0 + dd * (x1 - x0)**2 / 2.0)
		d = error / (x1 - x0)
		# Now, match the boundary conditions, because the above fit is really crummy.
		error = 1
		while abs(error) > 1e-9:
			cat = Catenary.from_x0y0ddd(x0, y0, d, dd)
			error = cat(x1) - y1
			slope = Catenary.deriv_d_x0y0ddd(x0, y0, d, dd, x1)
			d -= error / slope
		# Use Newton's method to zoom straight to the right answer.
		for alpha, num_rounds in newton_schedule:
			for i in xrange(num_rounds):
				cat = Catenary.from_x0y0ddd(x0, y0, d, dd)
				error = [cat.arc_length(x0, x1) - length, cat(x1) - y1]
				# Compute the Jacobian.
				arclen_gradient = Catenary.arclen_grad_x0y0ddd(x0, y0, d, dd, x0, x1)[1:]
				gradient = Catenary.gradient_x0y0ddd(x0, y0, d, dd, x1)
				# Invert the Jacobian, and multiply it by our error.
				k = solve_system([arclen_gradient, gradient], error)
				# Subtract the result off, making a Newton step.
				d -= k[0] * alpha
				dd -= k[1] * alpha
		return cat

	@staticmethod
	def deriv_d_x0y0ddd(x0, y0, d, dd, x):
		"""deriv_d_x0y0ddd(x0, y0, d, dd, x) -> value

		Gives D[Catenary.from_x0y0ddd(x0, y0, d, dd)(x), d].
		"""
		# paracurve = FullSimplify[catenary /. {xm -> gxm, ym -> gym, a -> gA}]
		# FullSimplify[D[paracurve, d]]
		f1 = lambda func, bound: func(dd * (bound - x0)/(1 + d**2)**0.5 + math.asinh(d))
		value = - 2 * (d + d**3)
		value += d * (1 + d**2)**0.5 * f1(math.cosh, x)
		value += (1 + d * (d - dd * x + dd * x0)) * f1(math.sinh, x)
		value /= (1 + d**2.0) * dd
		return value

	@staticmethod
	def deriv_dd_x0y0ddd(x0, y0, d, dd, x):
		"""deriv_dd_x0y0ddd(x0, y0, d, dd, x) -> value

		Gives D[Catenary.from_x0y0ddd(x0, y0, d, dd)(x), dd].
		"""
		# FullSimplify[D[paracurve, dd]]
		f1 = lambda func, bound: func(dd * (bound - x0)/(1 + d**2)**0.5 + math.asinh(d))
		value = 1 + d**2 - (1 + d**2)**0.5 * f1(math.cosh, x)
		value += dd * (x - x0) * f1(math.sinh, x)
		value /= dd**2
		return value

	@staticmethod
	def gradient_x0y0ddd(x0, y0, d, dd, x):
		return [getattr(Catenary, "deriv_%s_x0y0ddd" % s)(x0, y0, d, dd, x) for s in ("d", "dd")]

if __name__ == "__main__":
	start, stop, length = 0, 5, 10
	import time
	t0 = time.clock()
	cat = Catenary.from_ABl(start, 0, stop, -5, length)
	t1 = time.clock()
	print 1.0 / (t1 - t0)
	print cat(start)
	print cat(stop)
	print cat.arc_length(start, stop)

