#! /usr/bin/python
# All lengths are in meters.

import srt_solver

LATTICE_SPACING = 5.0 # Discretize every 10 cm of rope.
LITTLE_G = 0.5
SPRING_CONSTANT = 1.0
ROPE_STIFFNESS = 1.0
DAMPING_FACTOR = 0.98

class RopeSegment:
	def __init__(self, parent, x, y):
		self.p = parent
		self.x, self.y = x, y
		self.prev = self.next = None
		self.xv = self.yv = 0.0

	def pull(self, other, const):
		const = min(5, const)
		dx = other.x - self.x
		dy = other.y - self.y
		self.xv += dx * const
		self.yv += dy * const
		other.xv -= dx * const
		other.yv -= dy * const

	def de_extremize(self, DAMP):
		if not self.prev or not self.next:
			self.new_xv = self.xv
			self.new_yv = self.yv
			return
		avg_xv = (self.prev.xv + self.next.xv)/2.0
		avg_yv = (self.prev.yv + self.next.yv)/2.0
		dev_xv = self.xv - avg_xv
		dev_yv = self.yv - avg_yv
		self.new_xv = avg_xv + dev_xv * DAMP
		self.new_yv = avg_yv + dev_yv * DAMP

class Rope:
	def __init__(self, mat, x, y, length):
		self.mat = mat
		# Place all the points in one location to start with.
		self.segs = [RopeSegment(self, x+LATTICE_SPACING*i, y) for i in xrange(int(length/LATTICE_SPACING)+1)]
		# Link the points appropriately.
		for i in xrange(len(self.segs)-1):
			self.segs[i+1].prev = self.segs[i]
			self.segs[i].next = self.segs[i+1]

	def update(self, dt):
		# Accelerate each segment due to gravity.
		for seg in self.segs:
			seg.yv += LITTLE_G * dt
		# Tension all the segments.
		for i in xrange(len(self.segs)-1):
			a, b = self.segs[i], self.segs[i+1]
			# Compute the error in separation.
			d2 = ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5
			# Compute the amount of motion towards extension.
			sepd = (a.x - b.x) * (a.xv - b.xv) + (a.y - b.y) * (a.yv - b.yv)
			# Add a Hookean tensile force.
			a.pull(b, max(0, (d2-LATTICE_SPACING))*SPRING_CONSTANT*dt + max(0, sepd*ROPE_STIFFNESS*dt))
		# De-extremize the velocities.
#		DAMP = pow(DAMPING_FACTOR, dt)
#		for seg in self.segs:
#			seg.de_extremize(DAMP)
#		for seg in self.segs:
#			seg.xv = seg.new_xv
#			seg.yv = seg.new_yv
		# Move all the segments.
		for seg in self.segs:
			seg.x += seg.xv*dt
			seg.y += seg.yv*dt
		damp = pow(DAMPING_FACTOR, dt)
		# Unnaturally damp their motion.
		for seg in self.segs:
			seg.xv *= damp
			seg.yv *= damp

