#!/usr/bin/env python3
import sys, json

def radeonmem():
	out = {}
	used  = int(open("/sys/class/drm/card1/device/mem_info_vram_used").readline()[:-1])
	total = int(open("/sys/class/drm/card1/device/mem_info_vram_total").readline()[:-1])
	out["text"] = "{}G/{}G".format(
		round(used/1024/1024/1024, 1),
		round(total/1024/1024/1024, 1)
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
	radeonmem()
