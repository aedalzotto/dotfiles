#!/bin/sh
# Launch waybar with the config for the current dock state: docked (external present) shows the
# bar on the external only; mobile (laptop only) shows it on eDP-1 (auto-hidden by the helper).
# The dock-controller restarts this service on monitor hotplug so it re-picks the right config.
export HYPRLAND_INSTANCE_SIGNATURE=${HYPRLAND_INSTANCE_SIGNATURE:-$(ls -t "$XDG_RUNTIME_DIR/hypr" 2>/dev/null | head -1)}
if hyprctl -j monitors | jq -e 'any(.[]; .name != "eDP-1")' >/dev/null 2>&1; then
    exec waybar -c "$HOME/.config/waybar/config.docked"
else
    exec waybar -c "$HOME/.config/waybar/config.mobile"
fi
