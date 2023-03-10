#!/usr/bin/env python3
import sys, json
from subprocess import check_output, DEVNULL
from argparse import ArgumentParser
from time import sleep
from os import remove
from os.path import exists

UPDATE_TIMEOUT = 1800
UPDATE_SLEEP   = 5

def has_updates(updates):
	out = {}

	out["text"] = "{} update{} available".format(len(updates), "s" if len(updates) > 1 else "")
	out["alt"] = "update"

	tooltip_str = "Packages:\n"
	for update in updates:
		tooltip_str += update + '\n'

	tooltip_str = tooltip_str[:-1]

	out["tooltip"] = tooltip_str

	out["class"] = "custom-update"

	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()

def is_updated():
	out = {}
	out["text"] = ""
	out["alt"] = "updated"

	out["tooltip"] = "All packages updated"

	out["class"] = "custom-updated"
 
	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()

def fetch(fetch_cmd):
	out = {}
	out["text"] = "Fetching updates..."
	out["alt"] = "fetching"

	out["tooltip"] = "Fetching updates"

	out["class"] = "custom-fetch"
 
	sys.stdout.write(json.dumps(out) + '\n')
	sys.stdout.flush()
 
	# First, lets call 'checkupdates'
	checkupdates = ["checkupdates"]
	pacman_updates = check_output(checkupdates, stderr=DEVNULL, universal_newlines=True).split('\n')[:-1]

	aur_updates = []
	if(fetch_cmd != ""):
		aur_fetch = fetch_cmd.split(" ")
		try:
			aur_updates = check_output(aur_fetch, stderr=DEVNULL, universal_newlines=True).split('\n')
		except:
			pass

	return pacman_updates + aur_updates

def main(fetch_cmd, interval):
	try:
		remove("/tmp/updates.lck")
	except:
		pass

	while True:
		updates = fetch(fetch_cmd)
		if(len(updates) == 0):
			is_updated()
			sleep(interval)
			pass
		else:
			open("/tmp/updates.lck", "w")
			has_updates(updates)
			timeout = 0
			while(exists("/tmp/updates.lck")):
				sleep(UPDATE_SLEEP)
				timeout += UPDATE_SLEEP
				if(timeout == UPDATE_TIMEOUT):
					remove("/tmp/updates.lck")
			

if __name__ == "__main__":
	parser = ArgumentParser(description="Update module for waybar.")
	parser.add_argument('-f', "--fetchcmd", default="", help="Command to optionally fetch (only) AUR updates (e.g. paru -Qua).")
	parser.add_argument('-i', "--interval", type=int, default=3600, help="Number of seconds between each call. Default = 3600 (1 hour).")
	args = parser.parse_args()
 
	main(args.fetchcmd, args.interval)
