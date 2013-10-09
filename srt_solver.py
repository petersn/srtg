#! /usr/bin/python

import os, json, math

# XXX: For now catenaries are faked as parabolas!

# Half parabola arc length.
# Gives arc length from 0 to x on a*x^2.
def hpal(x, a):
	return (2*a*x*(1 + 4*a**2*x**2)**0.5 + math.asinh(2*a*x)) / (4*a)

def dhpalda(x, a):
	"""dhpalda(x, a) -> D[hpal(x, a), a]"""
	return (2*a*x*(1 + 4*a**2*x**2)**0.5 - math.asinh(2*a*x)) / (4*a**2)

def parabola_arc_length(x0, x1, params, hpal=hpal):
	"""parabola_arc_length(x0, x1, params) -> arc length between x0 and x1"""
	a, xm, ym = params
	l0, l1 = abs(hpal(x0-xm, a)), abs(hpal(x1-xm, a))
	# If both points are on the same side of the minimum, subtract the closer one.
	if (x0-xm) * (x1-xm) > 0:
		return max(l0, l1) - min(l0, l1)
	else:
		return l0 + l1

def darc_lengthda(x0, x1, params):
	"""darc_lengthda(x0, x1, params) -> D[parabola_arc_length(x0, x1, params), a]"""
	return parabola_arc_length(x0, x1, params, hpal=dhpalda)

def parabola(x, params):
	a, xm, ym = params
	return a * (x - xm)**2.0 + ym

def dparabola(x, params):
	a, xm, ym = params
	return 2 * a * (x - xm)

def fit_parabola(x0, y0, x1, y1, length):
	assert (x0-x1)**2 + (y0-y1)**2 < length**2
	assert x0 != x1
	# Start by guessing a totally generic curve parameter,
	# and that the lowest point is between x0 and x1.
	a, xm = 1.0, (x0+x1)/2.0
	old_xm = float("-inf")
	# Ten rounds of approximation.
	for IT in xrange(20):
		# Match the arc length constraint by varying a with Newton's method.
		for i in xrange(6):
			params = (a, xm, 0)
			error = parabola_arc_length(x0, x1, params) - length
			slope = darc_lengthda(x0, x1, params)
			a -= error / slope
		# Recenter the parabola to pass through both control points.
		xm = (a*(x0**2-x1**2) + y1 - y0) / (2*a*(x0-x1))
		if abs(xm-old_xm) < 1e-5:
			break
		params = (a, xm, 0)
		old_xm = xm
	# Finally, set ym to pass through both control points.
	ym = y0 - parabola(x0, params)
	return a, xm, ym

def parabola_energy(x0, x1, params):
	a, xm, ym = params
	return -((x0 - x1) * (a * (x0**2 + x0*x1 + x1**2 - 3*(x0+x1)*xm + 3*xm**2) - 3*ym))/3

def load_config_file(*path):
	"""load_config_file(*path) -> parsed json contents

	Parses a config file from data/
	"""
	fd = open(os.path.join("data", *path))
	data = fd.read()
	fd.close()
	o = []
	for line in data.split("\n"):
		line = line.split("#")[0].strip()
		if not line: continue
		o.append(line)
	data = "\n".join(o)
	return json.loads(data)

#rope_types = {}
#for key, value in load_config_file("ropes.txt").iteritems():
#	rope_types[key] = RopeType(key, value)

if __name__ == "__main__":
	params = fit_parabola(0, 0, 1, 1, 2)
	print params
	print parabola(0, params)
	print parabola(1, params)
	print parabola_arc_length(0, 1, params)

