#!/usr/bin/env python3
import sys, json

def radeonmem():
	out = {}
	out["text"] = "{}G/{}G".format(
		round(int(open("/sys/class/drm/card0/device/mem_info_vram_used").readline()[:-1])/1024/1024/1024, 1),
		round(int(open("/sys/class/drm/card0/device/mem_info_vram_total").readline()[:-1])/1024/1024/1024, 1)
	)
	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()	

if __name__ == "__main__":
	radeonmem()
