#! /usr/bin/env python3
import sys
from solaar.cli import run
from io import StringIO
from json import dumps

mouse_name = sys.argv[1]

original_stdout = sys.stdout
captured_output = StringIO()
sys.stdout = captured_output
run(['show'])
sys.stdout = original_stdout

result = captured_output.getvalue().splitlines()

name_line = None
bat_line = None
for i, line in enumerate(result):
    if name_line is None:
        if mouse_name in line:
            name_line = line
    elif line.strip().startswith('Battery: '):
        bat_line = line
        break

out = {}
if name_line is None or bat_line is None:
    out["text"]    = " "
    out["tooltip"] = f"Device not found"
    out["class"]   = "disconnected"
else:
    name    = name_line.split(':')[-1].strip()
    batinfo = bat_line.split(':')[-1].strip()
    battery = batinfo.split('%')[0]
    status  = batinfo.split('.')[-2]
    out["text"] = " "
    out["tooltip"] = f"{name}: {battery}%"
    out["percentage"] = int(battery)
    if status == "DISCHARGING":
        out["class"] = "normal"
        if int(battery) <= 16:
            out["class"] = "critical"
        elif int(battery) <= 33:
            out["class"] = "warning"
    elif status == "RECHARGING":
        out["text"] = " "
        out["class"] = "charging"
    else:
        out["text"] = " "
        out["class"] = "full"

sys.stdout.write(dumps(out) + '\n')
sys.stdout.flush()
