#!/usr/bin/env python3
"""Dock-aware laptop controller for Hyprland.

Listens to the Hyprland event socket and, based on whether an external display is present:
  - docked  : restart waybar onto the external only (config.docked); pin externals to bsod;
              dim the laptop OLED to DIM% while it's unfocused, un-dim when it's focused or
              showing a fullscreen window; stop the auto-hide helper.
  - mobile  : restart waybar onto eDP-1 (config.mobile); restore laptop brightness; start the
              auto-hide helper.

Written in Python (no socat) since python3 is already used across the waybar modules.
"""
import json
import os
import subprocess
import threading

EDP = "eDP-1"
DIM = 10                       # laptop backlight % while docked + unfocused
GRACE = 30                     # seconds unfocused before dimming
HELPER = "waybar-autohide.service"   # your auto-hide helper unit (edit if named differently)
BSOD = os.path.expanduser("~/Drive/Imagens/Wallpapers/bsod.png")

HIS = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
RUNTIME = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
if not HIS:  # fallback: newest instance dir
    hypr_dir = os.path.join(RUNTIME, "hypr")
    HIS = sorted(os.listdir(hypr_dir), key=lambda d: os.path.getmtime(os.path.join(hypr_dir, d)))[-1]
    os.environ["HYPRLAND_INSTANCE_SIGNATURE"] = HIS
SOCK = os.path.join(RUNTIME, "hypr", HIS, ".socket2.sock")


def run(*args):
    return subprocess.run(args, capture_output=True, text=True)


def hypr_json(what):
    r = run("hyprctl", "-j", what)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return []


def monitors():
    return hypr_json("monitors")


def is_docked():
    return any(m.get("name") != EDP for m in monitors())


def focused_monitor():
    for m in monitors():
        if m.get("focused"):
            return m.get("name")
    return None


def edp_has_fullscreen():
    edp_id = next((m["id"] for m in monitors() if m.get("name") == EDP), None)
    if edp_id is None:
        return False
    return any(c.get("monitor") == edp_id and c.get("fullscreen") for c in hypr_json("clients"))


def get_brightness():
    r = run("light", "-G")
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 100.0


def set_brightness(pct):
    run("light", "-S", str(pct))


def set_externals_bsod():
    for m in monitors():
        if m.get("name") != EDP:
            run("hyprctl", "hyprpaper", "wallpaper", f"{m['name']},{BSOD}")


def helper(action):
    run("systemctl", "--user", action, HELPER)  # no-op if the unit doesn't exist


class Controller:
    def __init__(self):
        self.docked = is_docked()
        self.saved = None          # laptop brightness captured on mobile->docked
        self.focused = focused_monitor()
        self.timer = None
        # apply the current state once at startup (launcher already picked the waybar config)
        if self.docked:
            self.saved = get_brightness()
            set_externals_bsod()
            helper("stop")
            self.reevaluate_dim()
        else:
            helper("start")

    # --- dim scheduling ---
    def cancel_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def schedule_dim(self):
        self.cancel_timer()
        self.timer = threading.Timer(GRACE, self.do_dim)
        self.timer.start()

    def do_dim(self):
        if not self.docked or self.focused == EDP or edp_has_fullscreen():
            return
        set_brightness(DIM)

    def undim(self):
        self.cancel_timer()
        if self.saved is not None:
            set_brightness(self.saved)

    def reevaluate_dim(self):
        """Decide the laptop panel state from current focus + fullscreen (docked only)."""
        if not self.docked:
            return
        if self.focused == EDP or edp_has_fullscreen():
            self.undim()
        else:
            self.schedule_dim()

    # --- events ---
    def on_monitor_change(self):
        now = is_docked()
        if now != self.docked:
            self.docked = now
            run("systemctl", "--user", "restart", "waybar")  # launcher re-picks config
            if now:
                self.saved = get_brightness()
                set_externals_bsod()
                helper("stop")
                self.focused = focused_monitor()
                self.reevaluate_dim()
            else:
                self.undim()
                helper("start")
        elif now:               # still docked, e.g. a 2nd external added
            set_externals_bsod()

    def on_focus(self, mon):
        self.focused = mon
        self.reevaluate_dim()

    def on_fullscreen(self):
        self.reevaluate_dim()


def _connect():
    import socket
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCK)
    return s.makefile("r")


def loop():
    ctl = Controller()
    stream = _connect()
    for line in stream:
        event, _, data = line.strip().partition(">>")
        if event in ("monitoradded", "monitoraddedv2", "monitorremoved"):
            ctl.on_monitor_change()
        elif event == "focusedmon":
            ctl.on_focus(data.split(",")[0])
        elif event == "fullscreen":
            ctl.on_fullscreen()


if __name__ == "__main__":
    loop()
