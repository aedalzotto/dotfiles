#!/bin/sh
#
# Address several issues with systemd user sessions
#
# 1. The common way to autostart a systemd service along with the desktop
#    environment is to add it to a `graphical-session.target`. However, systemd
#    forbids starting the graphical session target directly and encourages use
#    of an environment-specific target units. Therefore, the integration
#    package here provides and uses `sway-session.target` which would bind to
#    the `graphical-session.target`.
#
# 2. Stop the target and unset the variables when the compositor exits.
#
# References:
#  - https://www.freedesktop.org/software/systemd/man/systemd.special.html#graphical-session.target
#
SESSION_TARGET="hyprland-session.target"

# Check if another Sway session is already active.
#
# Ignores all other kinds of parallel or nested sessions
# (Sway on Gnome/KDE/X11/etc.), as the only way to detect these is to check
# for (WAYLAND_)?DISPLAY and that is know to be broken on Arch.
if systemctl --user -q is-active "$SESSION_TARGET"; then
    echo "Another session found; refusing to overwrite the variables"
    exit 1
fi

# reset failed state of all user units
systemctl --user reset-failed

# shellcheck disable=SC2086
systemctl --user start "$SESSION_TARGET"
