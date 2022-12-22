#!/usr/bin/env python3
import sys, json
from argparse import ArgumentParser
from subprocess import Popen, PIPE
from time import sleep

def gpu(top):
	out = {}
	out["text"] = int(float(top[1].split(" ")[1][:-1])) # GPU
	out["tooltip"] = \
		"Graphics pipe: {}%\n".format(out["text"]) + \
		"Event Engine: {}%\n".format(int(float(top[2].split(" ")[1][:-1]))) + \
		"Vertex Grouper + Tesselator: {}%\n".format(int(float(top[3].split(" ")[1][:-1]))) + \
		"Texture Addresser: {}%\n".format(int(float(top[4].split(" ")[1][:-1]))) + \
		"Shader Export: {}%\n".format(int(float(top[5].split(" ")[1][:-1]))) + \
		"Sequencer Instruction Cache: {}%\n".format(int(float(top[6].split(" ")[1][:-1]))) + \
		"Shader Interpolator: {}%\n".format(int(float(top[7].split(" ")[1][:-1]))) + \
		"Scan Converter: {}%\n".format(int(float(top[8].split(" ")[1][:-1]))) + \
		"Primitive Assembly: {}%\n".format(int(float(top[9].split(" ")[1][:-1]))) + \
		"Depth Block: {}%\n".format(int(float(top[10].split(" ")[1][:-1]))) + \
		"Color Block: {}%".format(int(float(top[11].split(" ")[1][:-1])))

	out["class"] = "custom-gpu"

	return out

def mem(top):
	out = {}
	usedPercent = float(top[12].split(" ")[1][:-1])
	usedRaw = float(top[12].split(" ")[2][:-2])
	total = round(float(usedRaw / usedPercent * 100) / 1024, 1)
	used = round(usedRaw / 1024, 1)

	out["text"] = "{}G/{}G".format(used, total)
	out["tooltip"] = "{}GiB used".format(used)

	out["class"] = "custom-mem"

	return out

def main(args):
	option = args.option
	cmd = ["radeontop", "-d", "-"]

	with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
		# Continuous monitor to avoid reopening overhead
		for line in p.stdout:
			try:	# First line should be ignored
				line = line.split(": ")[1]	# Eliminate the time and the first space
			except:
				continue

			top = line.split(", ")		# Separate keys

			if option == "gpu":
				out = gpu(top)
			elif option == "mem":
				out = mem(top)

			sys.stdout.write(json.dumps(out) + '\n')
			sys.stdout.flush()

if __name__ == "__main__":
	parser = ArgumentParser(description='Radeontop module for waybar.')
	subparsers = parser.add_subparsers(dest="option")
	gpu_parser = subparsers.add_parser("gpu", help="Get GPU usage info")
	mem_parser = subparsers.add_parser("mem", help="Get memory usage (GiB) info")
	
	args = parser.parse_args()
	main(args)
