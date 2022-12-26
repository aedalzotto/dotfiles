#!/usr/bin/env python3
import signal, sys, json
from os import getpid
from argparse import ArgumentParser

out = {}
option = ""

def change_mode(signum, frame):
	if signum == signal.SIGUSR1:
		out["alt"] = option
	else:
		out["alt"] = "laptop"
 
	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()

def tablet_dis():
	out["alt"] = "laptop"
 
	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()

def main():
	with open("/tmp/waybar-tablet-{}.pid".format(option), "w") as file:
		file.write(str(getpid()))

	out["text"] = ""
	out["alt"] = "laptop"
	out["class"] = "custom-{}".format(option)
	if option == "menu":
		out["tooltip"] = "Open application menu"
	elif option == "close":
		out["tooltip"] = "Close focused window"

	signal.signal(signal.SIGUSR1, change_mode)
	signal.signal(signal.SIGUSR2, change_mode)

	while True:
		signal.pause()

if __name__ == "__main__":
	parser = ArgumentParser(description="Update module for waybar.")
	subparsers = parser.add_subparsers(dest="option")
	subparsers.add_parser("menu", help="Application menu")
	subparsers.add_parser("close", help="Window close button")
	args = parser.parse_args()
	option = args.option
 
	main()
