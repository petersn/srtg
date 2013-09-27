#! /usr/bin/python

import os, json
import srt_solver

def sjwc(data):
	"""sjwc(data) -> [json objects]

	Parses Sequential Json With Comments.
	"""
	o = []
	for line in data.split("\n"):
		line = line.split("#")[0].strip()
		if not line: continue
		o.append(line)
	data = "\n".join(o)
	return json.loads(data)

# Load all the config files.
fd = open(os.path.join("data", "ropes.txt"))
data = fd.read()
fd.close()

ropes_data = sjwc(data)

print ropes_data

