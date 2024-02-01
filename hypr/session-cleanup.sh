#!/bin/sh
#
# Address several issues with systemd user sessions
#
# 1. Stop the target and unset the variables when the compositor exits.
#
# References:
#  - https://www.freedesktop.org/software/systemd/man/systemd.special.html#graphical-session.target
#

SESSION_SHUTDOWN_TARGET="hyprland-session-shutdown.target"

# stop the session target and unset the variables
systemctl --user start --job-mode=replace-irreversibly "$SESSION_SHUTDOWN_TARGET"
