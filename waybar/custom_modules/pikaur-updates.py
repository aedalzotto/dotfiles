#!/usr/bin/env python3
import sys, json, errno
from subprocess import check_output, DEVNULL, run, Popen
from argparse import ArgumentParser
from os import makedirs, getuid, symlink

def has_updates(number, updates):
	out = {}

	out["text"] = "Updates: {}".format(number)
	out["alt"] = "update"

	tooltip_str = "Packages:\n"
	for update in updates:
		tooltip_str += update + '\n'

	tooltip_str = tooltip_str[:-1]

	out["tooltip"] = tooltip_str

	out["class"] = "custom-update"

	return out

def is_updated():
	out = {}
	out["text"] = ""
	out["alt"] = "updated"

	out["tooltip"] = "All packages updated"

	out["class"] = "custom-updated"

	return out

def fetch():
	# First, lets call 'checkupdates'
	checkupdates = ["checkupdates"]
	pacman_updates = check_output(checkupdates, stderr=DEVNULL, universal_newlines=True).split('\n')[:-1]

	pikaur_Qua = ["pikaur", "-Qua"]
	aur_updates = check_output(pikaur_Qua, stderr=DEVNULL, universal_newlines=True).split('\n')[:-1]

	updates = pacman_updates + aur_updates
	number = len(updates)
	
	if number > 0:
		out = has_updates(number, updates)
	else:
		out = is_updated()

	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()

def main():
	fetch()

if __name__ == "__main__":
	parser = ArgumentParser(description="Pikaur updates module for waybar.")
	
	main()
