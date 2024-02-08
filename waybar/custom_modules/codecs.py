#!/usr/bin/env python3
from subprocess import check_output, run
from argparse import ArgumentParser
import sys
import json

def main(next, previous):
    cards = check_output(["pactl", "list", "cards"], universal_newlines=True)[:-1].split('\n')

    index = 0
    while cards[index + 1].split(' ')[1].split('.')[0] != "bluez_card":
        index += 1
        while cards[index].split(' ')[0] != "Card":
            index += 1

    index += 1
    card = cards[index].split(' ')[1]
    
    index += 1
    while cards[index].split(' ')[0] != "\tProfiles:":
        index += 1

    profiles = {}
    index += 1
    while cards[index].split(' ')[0] != "\tActive":
        profile = cards[index].split(' ')[0].split('\t')[2][:-1]
        codec = cards[index].split('(')[1].split(',')[1].split(' ')[2][:-1]
        if profile.split('-')[0] == "a2dp":
            profiles[profile] = codec
        index += 1

    active_profile = cards[index].split(' ')[2]
    
    if previous or next:
        keys = list(profiles.keys())
        active_idx = keys.index(active_profile)
        if next:
            active_idx += 1
        else:
            active_idx -= 1
        
        if active_idx >= len(keys):
            active_idx = 0
        elif active_idx < 0:
            active_idx = len(keys) - 1
        
        run(["pactl", "set-card-profile", card, keys[active_idx]])
    else:
        json_out = {
            'text': profiles[active_profile],
            'class': 'custom-' + profiles[active_profile],
            'tooltip': "Available codecs:\n\t"+"\n\t".join([profiles[profile] for profile in profiles])
        }

        output = json.dumps(json_out)
        sys.stdout.write(output + '\n')
        sys.stdout.flush()
    
if __name__ == '__main__':
    parser = ArgumentParser(description="Bluez codec switcher.")
    parser.add_argument('-n', "--next", action='store_true', help="Change to next codec")
    parser.add_argument('-p', "--previous", action='store_true', help="Change to previous codec")
    args = parser.parse_args()

    main(args.next, args.previous)
