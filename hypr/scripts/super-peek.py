#!/usr/bin/env python3
"""Show the auto-hidden waybar while a Super key is physically held (mobile mode only).

Why evdev instead of a Hyprland keybind: Hyprland suppresses a modifier's release bind once the
modifier is used in a combo (e.g. Super+1 to switch workspace), so a bind-based peek gets stuck
shown after any combo (open regression hyprwm/Hyprland#6946). Reading the key state straight from
evdev is immune to that. Requires membership in the 'input' group.

Uses waybar's directional signals (on-sigusr2=show / on-sigusr1=hide), so show/hide are idempotent
and don't fight the hover helper. Gated on the dock flag so it does nothing while docked.
"""
import os
import re
import struct
import subprocess
import threading

RUNTIME = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
DOCKFILE = os.path.join(RUNTIME, "dock-saved-brightness")  # exists => docked => peek disabled
META = {125, 126}          # KEY_LEFTMETA, KEY_RIGHTMETA
EV_KEY = 1
FMT = "llHHi"              # input_event: time(2x long), type u16, code u16, value i32  (24 bytes)
SIZE = struct.calcsize(FMT)

held = set()               # currently-pressed Super keycodes (across all keyboards)
lock = threading.Lock()


def signal_bar(name):
    if os.path.exists(DOCKFILE):   # docked: external bar stays visible, do nothing
        return
    subprocess.run(["pkill", f"-{name}", "-x", "waybar"])  # -x: don't also match waybar_auto_hide


def watch(path):
    try:
        f = open(path, "rb")
    except OSError:
        return
    while True:
        data = f.read(SIZE)
        if not data or len(data) < SIZE:
            return
        _, _, etype, code, val = struct.unpack(FMT, data)
        if etype != EV_KEY or code not in META or val == 2:   # ignore key-repeat (val 2)
            continue
        with lock:
            was_held = bool(held)
            held.add(code) if val == 1 else held.discard(code)
            now_held = bool(held)
            if now_held and not was_held:
                signal_bar("SIGUSR2")   # first Super down -> show
            elif was_held and not now_held:
                signal_bar("SIGUSR1")   # last Super up -> hide


def keyboards():
    devs = []
    for block in open("/proc/bus/input/devices").read().split("\n\n"):
        if "Handlers=" not in block or "kbd" not in block:
            continue
        m = re.search(r"Handlers=[^\n]*?(event\d+)", block)
        ev = re.search(r"EV=(\w+)", block)
        if m and ev and (int(ev.group(1), 16) >> EV_KEY) & 1:
            devs.append("/dev/input/" + m.group(1))
    return devs


def main():
    for dev in keyboards():
        threading.Thread(target=watch, args=(dev,), daemon=True).start()
    threading.Event().wait()   # block forever; threads do the work


if __name__ == "__main__":
    main()
