#!/bin/sh
# Rotate the laptop (eDP-1) wallpaper to a random 16:10 image; keep every external output on
# the original 16:9 bsod image. Fired by wallpaper-rotate.timer.
# ponytail: hyprpaper v0.8.4 `wallpaper` auto-loads; loaded set is bounded, so no unload needed.
export HYPRLAND_INSTANCE_SIGNATURE=${HYPRLAND_INSTANCE_SIGNATURE:-$(ls -t "$XDG_RUNTIME_DIR/hypr" 2>/dev/null | head -1)}
DIR="$HOME/Drive/Imagens/Wallpapers/16-10"
BSOD="$HOME/Drive/Imagens/Wallpapers/bsod.png"

IMG=$(find "$DIR" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) | shuf -n1)
[ -n "$IMG" ] && hyprctl hyprpaper wallpaper "eDP-1,$IMG"

# external displays always show the original 16:9 image
hyprctl monitors | awk '/^Monitor/{print $2}' | while read -r MON; do
    [ "$MON" = "eDP-1" ] || hyprctl hyprpaper wallpaper "$MON,$BSOD"
done
