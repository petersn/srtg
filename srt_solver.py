#! /usr/bin/python

import os, json
import catenary_solver
import srt_fe

LITTLE_G = 9.8

class RopeModel:
	def __init__(self, rope, c1, c2):
		self.rope, self.c1, self.c2 = rope, c1, c2

class StaticRopeModel(RopeModel):
	"""
	StaticRopeModel models the situation where a rope is hanging in a catenary between two constraints.
	"""
	def process(self):
		length = self.c2.s - self.c1.s
		self.xy1, self.xy2 = self.c1.get_xy(), self.c2.get_xy()
		self.cat = catenary_solver.Catenary.from_ABl(self.xy1[0], self.xy1[1], self.xy2[0], self.xy2[1], length)
#		self.c1.apply_force(

	def get_xy(self, s):
		x = self.cat.get_x_by_s(self.xy1[0], s-self.c1.s)
		y = self.cat(x)
		return x, y

class RopeConstraint:
	def __init__(self, s, xy, params=None):
		self.s, self.xy, self.params = s, xy, params

	def get_xy(self):
		return self.xy

class FreeConstraint(RopeConstraint):
	"""
	FreeConstraint models a point on the rope that can vary in position freely.
	This typically appears at the ends of the rope.
	"""

class PointConstraint(RopeConstraint):
	"""
	PointConstraint models the rope being perfectly affixed to an ideal anchor.
	Used mostly for debugging.
	"""

class PulleyConstraint(RopeConstraint):
	"""
	PointConstraint models the rope being perfectly affixed to an ideal anchor.
	Used mostly for debugging.
	"""
	def process(self):
		# Figure out the tensions on us.
		pass

class Rope:
	def __init__(self, material, length):
		self.material, self.length = material, length
		# Sorted list of RopeConstraints on the rope.
		self.constraints = [FreeConstraint(0, (0,0)), FreeConstraint(length, (0,0))]
		# self.models[i] handles the segment before self.constraints[i].
		# Invariant when properly built: len(self.models) == len(self.constraints)-1
		self.models = []

	def housework(self):
		"""housework() -> None

		Called after fiddling in various places to be more DRY.
		Currently:
			1) Sorts the constraint list.
		"""
		self.constraints.sort(key=lambda c: c.s)

	def rebuild_models(self):
		self.housework()
		self.models = []
		# Add a static model between each pair of constraints.
		for i in xrange(len(self.constraints)-1):
			c1, c2 = self.constraints[i], self.constraints[i+1]
			self.models.append(StaticRopeModel(self, c1, c2))
		for model in self.models:
			model.process()

	def constrain(self, constraint):
		# Eliminiate constraints that constrain the same exact position.
		for c in self.constraints[:]:
			if c.s == constraint.s:
				self.constraints.remove(c)
		self.constraints.append(constraint)
		self.housework()

	def get_xy(self, s):
		for model in self.models:
			if model.c1.s <= s <= model.c2.s:
				return model.get_xy(s)

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

