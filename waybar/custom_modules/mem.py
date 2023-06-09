#!/usr/bin/env python3
import sys, json

def mem():
	out = {}
	meminfo = open("/proc/meminfo").readlines()
	total   = int(meminfo[0].split(' ')[-2])
	free    = int(meminfo[1].split(' ')[-2])
	buffers = int(meminfo[3].split(' ')[-2])
	cached  = int(meminfo[4].split(' ')[-2])
	
	# https://access.redhat.com/solutions/406773
	used = total - (free + buffers + cached)

	out["text"] = "{}G/{}G".format(
		round(used/1024/1024, 1),
		round(total/1024/1024, 1)
	)

	percentage = used/total
	if percentage < 0.75:
		out["class"] = "normal"
	elif used/total < 0.9:
		out["class"] = "warning"
	else:
		out["class"] = "critical"

	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()	

if __name__ == "__main__":
	mem()
