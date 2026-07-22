#!/bin/sh
# Install the root-owned copies for Part D (external-keyboard backlight).
#
# The canonical sources live here in ~/.config (git-tracked). These are installed as COPIES,
# never symlinks: /usr/local/bin and /etc/udev/rules.d are executed by root, so pointing them
# at a file under $HOME (user-writable) would let any process running as the user rewrite code
# that root then runs — a local privilege-escalation hole. Re-run this after editing a source.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

sudo install -m 755 -o root -g root "$DIR/ext-kbd-backlight" /usr/local/bin/ext-kbd-backlight
sudo install -m 644 -o root -g root "$DIR/99-external-keyboard-backlight.rules" \
     /etc/udev/rules.d/99-external-keyboard-backlight.rules
sudo udevadm control --reload-rules

echo "Installed. udev rules reloaded."
