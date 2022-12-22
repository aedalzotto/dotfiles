#!/usr/bin/env python3
from subprocess import check_output, run
from argparse import ArgumentParser

def toggle_sinks():
	sinks = check_output(["pactl", "list", "sinks", "short"], universal_newlines=True)[:-1].split('\n')
	# print(len(sinks))

	for i in range (0, len(sinks)):
		if "RUNNING" in sinks[i]:
			active = i
			break

	next_sink = (i + 1) % len(sinks)
	sink_id = sinks[next_sink].split("\t")[0]

	run(["pactl", "set-default-sink", sink_id])

def main():
	toggle_sinks()

if __name__ == "__main__":
	parser = ArgumentParser(description="Pulseaudio sink toggler.")
	
	main()
