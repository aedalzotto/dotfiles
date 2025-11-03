#!/usr/bin/env python3
from subprocess import check_output, run
from argparse import ArgumentParser

def toggle_sinks():
	sinks = check_output(["pactl", "list", "sinks", "short"], universal_newlines=True)[:-1].split('\n')

	for i in range (0, len(sinks)):
		current_sink = sinks[i].split('\t')
		if current_sink[4] == "RUNNING" and current_sink[1] != "easyeffects_sink":
			active = i
			break

	next_sink = (i + 1) % len(sinks)
	next_sink_line = sinks[next_sink].split('\t')
	if next_sink_line[1] == "easyeffects_sink":
		next_sink = (next_sink + 1) % len(sinks)

	next_sink_line = sinks[next_sink].split('\t')
	sink_id = next_sink_line[0]

	run(["pactl", "set-default-sink", sink_id])

def main():
	toggle_sinks()

if __name__ == "__main__":
	parser = ArgumentParser(description="Pulseaudio sink toggler.")
	
	main()
