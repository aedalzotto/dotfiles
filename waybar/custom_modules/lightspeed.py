#! /usr/bin/env python3
import sys, re
from solaar.cli import run
from io import StringIO
from json import dumps

original_stdout = sys.stdout
captured_output = StringIO()
sys.stdout = captured_output
run(['show'])
sys.stdout = original_stdout

result = captured_output.getvalue()
match = re.search(r"  1: .*\n", result)
name = match.group().strip().split(": ")[1]
match = re.search(r"     Battery: .*\n", result)
bat = match.group().strip().split(" ")[1][:-2]

out = {}
out["text"] = ""
out["tooltip"] = f"{name}: {bat}%"
out["percentage"] = int(bat)
out["class"] = "normal"
if int(bat) <= 16:
    out["class"] = "critical"
elif int(bat) <= 33:
    out["class"] = "warning"

sys.stdout.write(dumps(out) + '\n')
sys.stdout.flush()
